from pynput import keyboard


def keypressed(key):
    if key == keyboard.Key.space:     
        print('space pressed')
    elif key == keyboard.Key.up:
        print('up pressed')
    elif key == keyboard.Key.down:      
        print('down pressed')
    elif key == keyboard.Key.left:
        print('left pressed')
    elif key == keyboard.Key.right:
        print('right pressed')
    elif key == keyboard.Key.esc:
        print('Escape')
        listener.stop() 

listener = keyboard.Listener(on_press=keypressed)
listener.start()
listener.join()

