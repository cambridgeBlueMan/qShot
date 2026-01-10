[← Back to Documentation](../README.md)

# Classifier

This component is a clone of an NVIDIA tool designed to collect images for Transfer Learning. (Transfer learning is a technique for re-training a DNN model on a new dataset. This typically takes less time than training a network from scratch. With transfer learning, the weights of a pre-trained model are fine-tuned to classify a customized dataset.)

For more detailed information on what we are trying to do here checkout this link

[NVIDIA Classification Tool](https://github.com/dusty-nv/jetson-inference/blob/master/docs/pytorch-collect.md)

# Preparation
Before we can start capturing images we need to define a folder to hold our images and a text file which will hold the labels for the various classes of objects we wish to train on. In our example we are going to train the model to recognise a variety of different Mamod Steam Engine accessories. thus our labels file would look something like:

```
background
black_grinder
bracket
bracket_worn
green_grinder
hammer_horiz
hammer_vert
motor
rectangular_plate
spanner
square_plate
tin
```

Note the inclusion of "background" as the first item in the list.

Use the Dataset Path and Class Labels `...` buttons to set values and then press the `init` button. 

The app will automatically create a folder structure as below:

````markdown
mamod/
├── train/
│   ├── background/
│   ├── black_grinder/
│   ├── bracket/
│   ├── bracket_worn/
│   ├── green_grinder/
│   ├── hammer_horiz/
│   ├── hammer_vert/
│   ├── motor/
│   ├── rectangular_plate/
│   ├── spanner/
│   ├── square_plate/
│   └── tin/
├── val/
│   ├── background/
│   ├── black_grinder/
│   ├── bracket/
│   ├── bracket_worn/
│   ├── green_grinder/
│   ├── hammer_horiz/
│   ├── hammer_vert/
│   ├── motor/
│   ├── rectangular_plate/
│   ├── spanner/
│   ├── square_plate/
│   └── tin/
└── test/
    ├── background/
    ├── black_grinder/
    ├── bracket/
    ├── bracket_worn/
    ├── green_grinder/
    ├── hammer_horiz/
    ├── hammer_vert/
    ├── motor/
    ├── rectangular_plate/
    ├── spanner/
    ├── square_plate/
    └── tin/
```
In addition to this the `Current Set` and `Current Class` drop down lists are now populated with the appropriate entries. So we are now ready to start capturing images knowing that the management of the data is being handled by the app.

# Where to go from here