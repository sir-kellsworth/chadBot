from pynput import mouse, keyboard
import time

#**************************************************************************
def onMove(x, y):
    print((x, y))

mouseListener = mouse.Listener(
    on_move=onMove,
    on_click=None,
    on_scroll=None
)

mouseListener.start()
while True:
    time.sleep(5)
mouseListener.stop()
