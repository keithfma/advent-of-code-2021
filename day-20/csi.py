import typing as T
import numpy as np



EnhanceMap = T.NewType('EnhanceMap', T.Mapping[str, bool])


def parse_input(filename: str) -> T.Tuple[np.ndarray, EnhanceMap]:

    
    with open(filename, 'r') as fp:
        enhance_txt = fp.readline().strip()
        fp.readline()
        image_txt = fp.read().strip()

    # convert image to character array for easy scanning
    image_arr = np.array([list(line) for line in image_txt.split('\n')])

    # convert enhancement key to mapping
    # note: a 9-bit integer can represent 0-511
    enhance_map = dict()
    for idx in range(512):
        key = format(idx, '09b').replace('0', '.').replace('1', '#')
        enhance_map[key] = enhance_txt[idx]

    return image_arr, enhance_map


def enhance_image(image: np.ndarray, lookup: EnhanceMap, num_iter: int) -> np.ndarray:

    # decide what value to pad with
    if lookup['.........'] == '#' and lookup['#########'] == '.':
        # infinite pad will flicker
        pad_input = '.#'[num_iter % 2]
        pad_output = '.#'[(num_iter+1) % 2]
    else:
        pad_input = pad_output = '.'

    # pad with 5-elements of 0's
    # we need the pad to be large enough to account for all lit pixels in the 
    #   infinite domain
    image = np.pad(image, 3, mode='constant', constant_values=pad_input)

    # convert pad value

    # compute enhanced value for all interior pixels 
    enhanced = np.full(image.shape, pad_output)
    for ii in range(1, image.shape[0] - 1):
        for jj in range(1, image.shape[1] -1):
            window = image[ii-1:ii+2, jj-1:jj+2]
            key = ''.join(window.ravel())
            enhanced[ii, jj] = lookup[key]

    # strip off unpopulated padding and return
    return enhanced



def display(image: np.ndarray):
    lines = []
    for ii in range(image.shape[0]):
        lines.append(''.join(image[ii, :]))
    print()
    print('\n'.join(lines))
    print()


def count(image: np.ndarray) -> int:
    return np.sum(image == '#')


if __name__ == '__main__': 
    
    # input_file = 'test_input.txt'
    input_file = 'input.txt'


    print('puzzle 1 -----------')
    img, key = parse_input(input_file)
    for niter in range(2):
        img = enhance_image(img, key, niter)
    print(f'Number of lit pixels: {count(img)}')
    print()

    print('puzzle 2 -----------')
    img, key = parse_input(input_file)
    for niter in range(50):
        print(img.shape)
        img = enhance_image(img, key, niter)
    print(f'Number of lit pixels: {count(img)}')
    print()
