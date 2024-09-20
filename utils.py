
import arcade
from arcade.experimental.texture_render_target import RenderTargetTexture
import os
import numpy as np

def load_program(filepath, ctx): # loads rendering program
    if(filepath[filepath.rfind('/')+1:] not in os.listdir(filepath[:filepath.rfind('/')])): # programs are stored in one directory for simplicity
        print(os.listdir(filepath[:filepath.rfind('/')]))
        print("missing --" + filepath[filepath.rfind('/'):] + "-- shader directory")
        return
    files = os.listdir(filepath)
    file_extensions = [file[file.rfind('.'):] for file in files]

    if(".vert" not in file_extensions): # requires vertex shader
        print(files)
        print("missing --" + filepath + "-- vertex shader")
        
    file_types = [".vert", ".geo", ".frag"]
    loaded_files = []
    for typ in file_types: # loads each type of shader in order
        if typ in file_extensions:
            with open(filepath + '/' + files[np.argmax([ext == typ for ext in file_extensions])]) as program_file:
                loaded_files.append(program_file.read())
        else:
            loaded_files.append(None)


    return ctx.program( # comlpiles loaded shader to program
        vertex_shader=loaded_files[0],
        geometry_shader=loaded_files[1],
        fragment_shader=loaded_files[2]
    )

class Filter(RenderTargetTexture): # post processing effects

    def __init__(self, width, height, filepath):
        super().__init__(width, height)
        self.program = load_program(filepath, self.ctx)
        self.texture.wrap_x = self.ctx.CLAMP_TO_EDGE
        self.texture.wrap_y = self.ctx.CLAMP_TO_EDGE
            #self.fbo = ctx.framebuffer(color_attachments=[])
    
    def use(self):
        self._fbo.use()

    def draw(self):
        self.texture.use(0)
        self._quad_fs.render(self.program)
