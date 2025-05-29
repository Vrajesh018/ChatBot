import threading
import queue
from audio_utils import Recognizer
from gui_utils import App

# Create two queues
queue_front_to_back = queue.Queue()
queue_back_to_front = queue.Queue()
Recognizer_instance = Recognizer()
# Start backend thread
backend_thread = threading.Thread(
    target=Recognizer_instance.backend_loop,
    args=(queue_front_to_back, queue_back_to_front),
    daemon=True
)
backend_thread.start()

app = App(queue_front_to_back, queue_back_to_front)
app.mainloop()
