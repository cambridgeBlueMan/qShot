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

# Workflow

## 1 Set paths for dataset and class labels, and initialise


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

### 2 Select category (train, val or test) and image class 

Use the drop down boxes marked Current Set and Current Class to define which image set you wish to work with.

### Set Image Size

for best results with standard pretrained ResNet-18 models an image size of 224X224 pixels (RGB) is recommended. However the preview image at this size looks a bit ropey. It is possible to preview at any image size up to 512 X 512. Use the Square Size slider to adjust.

If you want the collected images to resample down to 244 X 244 when they are saved then tick the Resample on save option box.

# Where to go from here