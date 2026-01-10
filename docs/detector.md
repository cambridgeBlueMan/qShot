[← Back to Documentation](../README.md)

# Detector

This component creates datasets datasets in Pascal VOC format (which is supported during training).



This component is a clone of an NVIDIA tool designed to collect images for Transfer Learning. (Transfer learning is a technique for re-training a DNN model on a new dataset. This typically takes less time than training a network from scratch. With transfer learning, the weights of a pre-trained model are fine-tuned to classify a customized dataset.)

For more detailed information on what we are trying to do here checkout this link

[NVIDIA Classification Tool](https://github.com/dusty-nv/jetson-inference/blob/master/docs/pytorch-collect.md)

The Detector component uses AI techniques to locate and identify objects or regions of interest within images or video streams. Unlike classifiers, which assign a single label to an entire image, detectors provide both the class and the position (bounding box) of each detected object.

## AI Roots
Object detection is a major field in AI and computer vision. Modern detectors use deep learning models such as YOLO (You Only Look Once), SSD (Single Shot MultiBox Detector), or Faster R-CNN to process images and output both class labels and coordinates.

## Usage
- Highlight or track objects in real time
- Enable automation based on detected objects (e.g., trigger events)
- Support applications like surveillance, robotics, and smart cameras

The performance of the detector depends on the underlying model and the data it was trained on. For more on AI detection, see resources on object detection and deep learning.

[← Back to Documentation](../README.md)