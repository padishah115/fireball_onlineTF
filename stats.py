import numpy as np
from typing import List, Tuple

# STATISTICS 
def arrays_stats(arrays:List[np.ndarray])->Tuple[np.ndarray,np.ndarray]:
    """Performs statistical calculation on some list of arraylike objects,
    returning mean and standard deviation information.
    
    Paramters
    ---------
        arrays : List[np.ndarray]
            List of the arrays over whom we want to perform statistical calculations.
    
    Returns
    -------
        mean_arr : np.ndarray
            Array which encodes mean data at each position.
        std_arr : np.ndarray
            Array which encodes std at each position.
    """

    #Initialize stack using the first array in the list
    stack = arrays[0]

    #ITERATIVELY ADD REST OF ARRAYS TO THE STACK ALONG THE ZEROTH DIMENSION 
    #TO PRODUCE STACK OF SHAPE (LEN(ARRAYS), (ORIGINAL STACK SHAPE))
    for arr in arrays[1:]:
        stack = np.stack([stack, arr], axis=0)

    #Array of mean values, produced by calculating mean across axis 0
    mean_arr = np.multiply(np.sum(stack, axis=0), 1/len(arrays))
    #Array of std values, produced by calculating std across axis 0
    std_arr = np.std(stack, axis=0)

    return mean_arr, std_arr