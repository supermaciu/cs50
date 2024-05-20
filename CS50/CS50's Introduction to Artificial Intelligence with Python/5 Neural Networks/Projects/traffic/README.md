There are many ways to solve this traffic signs recognition computer vision problem.
My approach was to take inspiration from the lecture source code, the handwriting.py
script to be precise. Those two programs have similar data sets - the only
difference is that images in this traffic problem have colors, so you need to take
into account 3 color values for every pixel. The process in my head was:

1. Take the inputs.
2. Make many different filters to catch different features of the image.
3. Average pool the image with pool size 2x2 because I think it works better for
colors.
4. Flatten the units to transform this array to be one dimensional to make it
easier for the next layer to process the data.
5. Create a dense layer with as many neurons as there are color values for every pixel
in each row before the pooling. It works better then taking the number of pixels after
the pooling (divided by 4 because of 2x2 pool size). I think it's because of the power
of the whole neural network.
6. Create a dropout layer to prevent overfitting. The 0.25 value worked best.
7. Create a output layer to give results.