
def M(arr,i,j):
        # minor of a matrix (ith row, jth column removed)
        # https://stackoverflow.com/questions/3858213/numpy-routine-for-computing-matrix-minors

        return arr[np.array(list(range(i))+list(range(i+1,arr.shape[0])))[:,np.newaxis],
                np.array(list(range(j))+list(range(j+1,arr.shape[1])))]

def center_radius(self, t1):
    # finds center and radius of a 3-points PCB_ARC track
    #
    # https://math.stackexchange.com/questions/2836274/3-point-to-circle-and-get-radius
    # TODO: implement one of these:
    # https://en.wikipedia.org/wiki/Circumscribed_circle#Circumcircle_equations

    ### NOTE: not needed, PCB_ARC does have GetCenter() method
    p1 = t1.GetStart() 
    p2 = t1.GetMid() 
    p3 = t1.GetEnd()

    #m1, k1 = self.line(p1,p2)
    #m2, k2 = self.line(p2,p3)

    # perpendiculars
    #l1p
    
    # center
    c = pcbnew.wxPoint(0,0)

    return c