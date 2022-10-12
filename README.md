# DisQStress
### A simple widget that can be embedded in any `PyQt6`/`PySide6` project to help uncover latent stress points

The purpose of DisQStress is to generate dialable background noise to help uncover latent stress points in any `PyQt`/`PySide` application. The background noise will fill up the Signal/Slot queue and make it immediately obvious as to which Signals are holding up the queue and which should take priority in your application.

DisQStress will also help mimic low powered machines without having to spin up VMs or switch between environments.


### How to Use
Simply import `DisQStress`, place it in your main `__init__` and `.show()` it.
```
import DisQStress

class Window(QWidget):

    def __init__(self):
        stress = DisQStress.StressTest()
        stress.show()
```
The DisQStress application window will open alongside your main application.


## Actions
### Snake
The `Snake` action will operate like a traditional snake by progressing through the gride. A snake will be generated for every button click.

[Snake](https://user-images.githubusercontent.com/12412157/195205509-21fe50b5-845d-4e53-939a-5b0e1a3f2ad8.mp4)

### Wash
The `Wash` action will progressivly "wash" down the screen. A "wash" will be generated for every button click.

[Wash](https://user-images.githubusercontent.com/12412157/195205615-a981cf62-6370-468e-9619-792a317c2123.mp4)

### Rain
The `Rain` action will generate three simulated raindrops per click. The raindrops will appear at random intervals. Three raindrops will be generated for every button click.

[Rain](https://user-images.githubusercontent.com/12412157/195205654-88e5a99a-a59e-4fa1-9bc7-fd529f1a517f.mp4)

### Talk
Places a message in the status bar. This is intended to show the responsiveness of the `click` action in regards to whatever is going on in the grid.
### Mouse (Hovering, Hovered, Clicking, Clicked)
Hovering over a panel will turn the panel red with the respective coordinates being placed in the status bar.
Leaving the panel will active a hovered action that will update the status bar and restore the panel to the default state. The hovered status will be deleted after 1 second.
Clicking on a panel will update the status for the duration of the click as well as turn the panel red. Releasing the mouse will update the status bar but leave the panel in the `clicked` state.

[Everything](https://user-images.githubusercontent.com/12412157/195205723-2e12dd04-a9ea-4244-9681-c553a4eaa404.mp4)
