## Sender test

Sender randomly chooses led and also randomly decides to turn it on or off. Then it sends such a decision to CAN bus via CAN2 interface. Code to launch it:

```python
from can import sender


sender.run_led_disco()
```

## Receiver test

Receiver listens CAN1 interface (FIFO 0), receives data and inteprets it. Data contains led id and on/off state sent from sender. Code to launch it:

```python
from can import receiver


receiver.run_signal_listener()
```

## Twin CAN transceiver board test

This test sends data through CAN2 interface and reads it back via CAN1 and prints it. In case of separate CAN transceivers - they both should be connected to the same PyBoard.


```python
from can import twin


twin.run_twin_test()
```
