import gradio as gr
import enc

def processFrames(frames, fps, lines, pulselength):
    enc.video2audio(frames, fps, lines, pulselength)
    return "DONE!"


menu = gr.Interface(
    fn=processFrames,
    inputs=[gr.File(file_count="multiple", file_types=["image"]), gr.Slider(3, 30, value=10, step=1), gr.Slider(50, 250, value=150, step=10), gr.Slider(0, 1, value=0.2, step=0.1)],
    outputs="text").launch(inbrowser=True, show_error=True)

if __name__ == "__main__":
    menu.launch(share=True)
