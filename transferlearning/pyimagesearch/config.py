# import the necessary packages
import os

# initialize the path to the *original* input directory of images
ORIG_INPUT_DATASET = "transferlearning/plastics"

# initialize the base path to the *new* directory that will contain
# our images after computing the training and testing split
BASE_PATH = "transferlearning/dataset"

# define the names of the training, testing, and validation
# directories
TRAIN = "training"
TEST = "evaluation"
VAL = "validation"

# initialize the list of class label names
CLASSES = ["bead", "fiber"]

# set the batch size
BATCH_SIZE = 32

# initialize the label encoder file path and the output directory to
# where the extracted features (in CSV file format) will be stored
LE_PATH = os.path.sep.join(["transferlearning/output", "le.cpickle"])
BASE_CSV_PATH = "transferlearning/output"

# set the path to the serialized model after training
MODEL_PATH = os.path.sep.join(["transferlearning/output", "model.cpickle"])