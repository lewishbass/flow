
import arcade
from arcade.gl import BufferDescription
from array import array

from utils import load_program, Filter

import numpy as np
import time

 # Lewis Bass lewisbass@vt.edu
 # a fun little shader based eularian fluid simulation
 # based loosly off these two tutorials
 #  https://matthias-research.github.io/pages/tenMinutePhysics/17-fluidSim.pdf
 #  https://api.arcade.academy/en/latest/examples/game_of_life_fbo.html
 # WARNING: can be resource intensive, change sim_res_x, sim_res_y to improve performance


class Simulation(arcade.Window):

    def on_key_press(self, key, modifiers): # keyboard event handlers
        self.key_states[key] = True
        if key == arcade.key.ESCAPE:
            arcade.exit()

    def on_key_release(self, key, modifiers): # keyboard event handlers
        self.key_states[key] = False
        if key == arcade.key.SPACE:
            self.pause = not self.pause

    def __init__(self, width, height):
        self.key_states = {} # tracks key states

        self.shader_dir = "shaders" # directory all shaders are stored in

        self.lf = time.time()
        self.frame_num = 0
        self.pause = False

        super().__init__(width, height, "Flow Simulation", gl_version=(4, 3), resizable=False)
        self.ctx.enable(self.ctx.BLEND)
        self.center_window()
        
        # loads post processing filters
        self.chromabbr = Filter(self.width, self.height, self.shader_dir + '/' + "chromabbr")
        self.chromabbr.program['width'] = -0.01
        self.blur = Filter(self.width, self.height, self.shader_dir + '/' + "blur")
        self.blur.program['width'] = 0.03
        self.blur.program['resolution'] = 0.001
        self.theta = 0


        # fullscreen quad all images are rendered to
        self.quad_fs = arcade.gl.geometry.quad_2d_fs() # quad covering screen
        self.fluid_show = load_program(self.shader_dir + '/' + "fluidshow", self.ctx)
        self.background = load_program(self.shader_dir + '/' + "background", self.ctx)
        self.stream = load_program(self.shader_dir + '/' + "stream", self.ctx)

        # Flowstream origins
        streamx = 16*8
        streamy = 16*8
        buffer_format = "4f 4f"
        attributes = ["in_vert", "in_color"]
        initial_streams = np.vstack((
            [(i% streamx)/streamx*self.width for i in range(streamx*streamy)]  , # x
            [(i//streamx)/streamy*self.height for i in range(streamx*streamy)]  , # y
            [0                    for i in range(streamx*streamy)]  , # z
            [1                    for i in range(streamx*streamy)]  , # h
            np.random.rand(streamx*streamy)*255                     , # r
            np.random.rand(streamx*streamy)*255                     , # g
            np.random.rand(streamx*streamy)*255                     , # b
            np.ones(streamx*streamy)                                  # a
        )).transpose().flatten()
        
        self.stream_points0 = self.ctx.buffer(data = array('f', initial_streams))
        self.stream_points1 = self.ctx.buffer(reserve = self.stream_points0.size)
        self.stream_geo0 = self.ctx.geometry([BufferDescription(self.stream_points0, buffer_format, attributes)])
        self.stream_geo1 = self.ctx.geometry([BufferDescription(self.stream_points1, buffer_format, attributes)])
        self.stream['speed'] = 10
        self.stream['length'] = 100
        self.stream['skip'] = 20
        self.stream_compute = self.ctx.compute_shader(source = open(self.shader_dir + '/' + "stream.comp").read())
        self.stream_compute['speed'] = 0.1
        self.stream_compute['length'] = 40

        self.sim_res_x = 1000
        self.sim_res_y = 1000
        
        # init textures
        # fluid format   vx,   vy,   temp
        self.fluid = self.ctx.texture((self.sim_res_x, self.sim_res_y), components=3, dtype='f4', filter=(self.ctx.NEAREST, self.ctx.NEAREST), wrap_x=self.ctx.CLAMP_TO_EDGE, wrap_y=self.ctx.CLAMP_TO_EDGE)
        self.press = self.ctx.texture((self.sim_res_x, self.sim_res_y), components=3, dtype='f4', filter=(self.ctx.NEAREST, self.ctx.NEAREST), wrap_x=self.ctx.CLAMP_TO_EDGE, wrap_y=self.ctx.CLAMP_TO_EDGE)
        self.gauss = self.ctx.texture((self.sim_res_x, self.sim_res_y), components=3, dtype='f4', filter=(self.ctx.NEAREST, self.ctx.NEAREST), wrap_x=self.ctx.CLAMP_TO_EDGE, wrap_y=self.ctx.CLAMP_TO_EDGE)
        self.fluid.write(array('f', np.zeros(self.sim_res_x*self.sim_res_y*3)))

        # attach textures to rendering targets
        self.fb_fluid = self.ctx.framebuffer(color_attachments=[self.fluid])
        self.fb_press = self.ctx.framebuffer(color_attachments=[self.press])
        self.fb_gauss = self.ctx.framebuffer(color_attachments=[self.gauss])

        # load simulation shaders
        self.press_sim = load_program(self.shader_dir + '/' + "pressure" , self.ctx)
        self.gauss_sim = load_program(self.shader_dir + '/' + "gauss"    , self.ctx)
        self.advec_sim = load_program(self.shader_dir + '/' + "advection", self.ctx)

        self.gauss_sim['texture0'] = 0
        self.gauss_sim['texture1'] = 1
        self.gauss_sim['texture2'] = 2
        self.gauss_sim['over'] = 1.0 # overrelaxation

        # smoke emitter
        self.smoke_in = self.ctx.texture((self.sim_res_x, self.sim_res_y), components=3, dtype='f4', filter=(self.ctx.NEAREST, self.ctx.NEAREST), wrap_x=self.ctx.CLAMP_TO_EDGE, wrap_y=self.ctx.CLAMP_TO_EDGE)
        self.smoke_in.write(array('f', 
                                  self.gen_initial_data(self.sim_res_x, self.sim_res_y, self.sim_res_x/4  , self.sim_res_y/12, 20, 0.5, 0)+
                                  self.gen_initial_data(self.sim_res_x, self.sim_res_y, self.sim_res_x/4*3, self.sim_res_y/12, 20, 0.5, 0)+
                                  self.gen_initial_data(self.sim_res_x, self.sim_res_y, self.sim_res_x/2  , self.sim_res_y/8 , 30, 0.5, 0)
                                  ))
        

        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()



    def gen_initial_data(self, width, height, left, bottom, r, v, l):
        np.random.seed(2)
        a = np.zeros((height, width))
        b = np.zeros((height, width, 3))
        y = np.matmul(np.matrix(np.arange(height)).transpose(), np.matrix(np.ones(width)))
        x = np.matmul(np.matrix(np.ones(height)).transpose(), np.matrix(np.arange(width)))
        a[np.square(x-left)+np.square(y-bottom)<r*r] = v
        b[:, :, l] = a
        return b.flatten()
        


    def on_draw(self):
        cf = time.time()
        dt = cf-self.lf
        self.lf = cf
        self.frame_num +=1
        #if self.frame_num%10 == 0:
        #    print(1/dt)

        if(self.key_states.get(arcade.key.W, False)):
            self.theta += 2*np.pi*dt
        if(self.key_states.get(arcade.key.S, False)):
            self.theta -= 2*np.pi*dt

        
        if not self.pause:

            for i in range(40): # run 40 steps of pressure equalization
                self.fluid.use(0)
                self.press.use(1)
                self.smoke_in.use(2)

                self.fb_press.use()
                self.quad_fs.render(self.press_sim) # calculate individual divergence
                
                self.fb_gauss.use()
                self.quad_fs.render(self.gauss_sim) # balance outputs

                self.fluid   , self.gauss    = self.gauss   , self.fluid
                self.fb_fluid, self.fb_gauss = self.fb_gauss, self.fb_fluid # swap and repeat

            
            self.fluid.use(0)
            self.fb_gauss.use()
            self.fb_gauss.clear()

            self.advec_sim['speed'] = 0.5
            self.quad_fs.render(self.advec_sim) # advect velocities
            
            self.fluid   , self.gauss    = self.gauss   , self.fluid
            self.fb_fluid, self.fb_gauss = self.fb_gauss, self.fb_fluid

        # apply post processing filters
        self.chromabbr.clear()
        self.chromabbr.use()

        self.quad_fs.render(self.background)

        self.fluid.use()
        self.quad_fs.render(self.fluid_show)

        self.stream_points0.bind_to_storage_buffer(binding=0)
        self.stream_points1.bind_to_storage_buffer(binding=1)
        self.stream_compute.run(group_x=16*4*16, group_y=16)
        self.stream_points0, self.stream_points1 = self.stream_points1, self.stream_points0
        self.stream_geo0, self.streamgeo1 = self.stream_geo1, self.stream_geo0
        self.stream_geo0.render(self.stream)

        self.blur.clear()
        self.blur.use()
        self.chromabbr.draw()
        
        self.clear()
        self.use()
        self.blur.program['dx'] = np.cos(self.theta)
        self.blur.program['dy'] = np.sin(self.theta)
        self.blur.program['time'] = cf%10000
        self.blur.draw()



        


app = Simulation(1000, 1000)
arcade.run()
