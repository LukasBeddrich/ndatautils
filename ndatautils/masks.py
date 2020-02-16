# -*- coding: utf-8 -*-

###############################################################################
####################        IMPORTS        ####################################
###############################################################################

import matplotlib.pyplot as plt
from matplotlib.cm import Greys
from numpy import abs, arctan2, bool, deg2rad, float, nansum, reshape, sqrt, sum, ogrid, where, zeros
from math import pi

###############################################################################
###############################################################################

class Mask_Base:
    """
    Mask_Base class to generate basic mask object and support some functionality
    """
    
    def __init__(self, nn = 128, instrument = 'MIRA'):
        """
        Constructor of any Mask_Base objects.
        --------------------------------------------------
        
        Arguments:
        ----------
        nn          : int   : mask array with dimension nn x nn
        instrument  : str   : specifies the instrument to access Instrument parameter dictionary
                              'MIRA', 'RESEDA', 'RESEDAlegacy'
        
        Return:
        ----------
        obj         : Mask_Base     : Mask_Base object
        """
        
        self.nn = nn
        self.d_SD, self.s_SD_err, self.d_SD_unit = Instrument.get_Parameters(instrument, 'distance_SD')['distance_SD'] # sample-detector-distance in meters --> in Instrument class
#        self.pixelsize, self.pixelsize_err, self.pixelsize_unit = Instrument.get_Parameters(instrument, 'pixelsize')['pixelsize']
        self.pixelsize = 0.0015625 # dimension of a quadratic pixel of the CASCADE detector --> build into instrument class
        self.mask = zeros((self.nn, self.nn), dtype = float)
        self.masktype = 'Mask_Base'
        self.instrument = instrument
        
#------------------------------------------------------------------------------
        
    def __repr__(self):
        """
        Official string description.
        --------------------------------------------------
        
        Arguments:
        ----------
        self        :               : 
            
        Return:
        ----------
        desc_str    : str           : description of the object
        """
        
        return '{}x{} {} for {} data'.format(str(self.nn), str(self.nn), self.masktype, self.instrument)

#------------------------------------------------------------------------------

    def getMask(self):
        """
        Returns array representation of the mask.
        --------------------------------------------------
        
        Arguments:
        ----------
        self        :               : 
            
        Return:
        ----------
        self.mask   : ndarray   : array representation
        """
        
        return self.mask

#------------------------------------------------------------------------------

    def shape(self):
        """
        Returns shape/dimensions of the mask
        --------------------------------------------------
        
        Arguments:
        ----------
        self        :               : 
            
        Return:
        ----------
        shape       : tuple     : dimensions of the masks array representation
        """
        return (self.nn,)*2

#------------------------------------------------------------------------------

    @staticmethod
    def combine_masks(pres, posts, non_bool = True):
        """
        DEPRECIATED function!
        
        mainly for visualization purpose
        pres and posts are Pre_mask or Post_sector_mask instances
        combines [pre1, pre2, ..., pren] and [post1, post2, ..., postm] to
        [[pre1 * post1, pre1 * post2 , ..., pre1 * postm], [..., pre2 * postm],...[..., pren * postm]]
        """
        comb_masks = []
        for pre in pres:
            line = []
            for post in posts:
                if non_bool:
                    line.append(pre.getMask() * post.getMask())
                else:
                    line.append(pre.getboolMask() * post.getMask())
            comb_masks.append(line)
        return comb_masks

#------------------------------------------------------------------------------

    @staticmethod
    def show_mask(m_array, title = None):
        """
        Fast visualization tool for the mask array.
        --------------------------------------------------
        
        Arguments:
        ----------
        m_array     : ndarray       : 2D mask array to be visualized
        titel       : str / None    : titel of graphic, if provided 
        
        Return:
        ----------
        None
        """
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(m_array, cmap = Greys, origin = 'lower')
        ax.set_xlabel('Pixel')
        ax.set_ylabel('Pixel')
        if title is not None: ax.set_title('{}'.format(title))
        return None


###############################################################################
###############################################################################

class Grid_mask(Mask_Base):
    """
    Grid_Mask class for pre-grouping Cascade Detector pixel with quadratic tiles.
    Subclass of Mask_Base
    """
    
    def __init__(self, tile_size, nn, instrument):
        """
        Constructor of a Grid_mask objects.
        --------------------------------------------------
        
        Arguments:
        ----------
        tile_size   : int           : dimensions of the tiles, which build up the grid
        nn          : int           : mask array with dimension nn x nn
        instrument  : str           : specifies the instrument to access Instrument parameter dictionary
                                      'MIRA', 'RESEDA', 'RESEDAlegacy'
        
        Return:
        ----------
        obj         : Grid_mask     : 
        """

        Mask_Base.__init__(self, nn, instrument)
        self.masktype = 'Grid_mask'
        
        if nn % tile_size == 0:
            self.tile_size = tile_size
        else:
            print('tile_size is not a divisor of nn! tile_size set to 1.')
            self.tile_size = 1
        
        self.create_grid_mask()

#------------------------------------------------------------------------------

    def create_grid_mask(self):
        """
        Creates tiled Grid_mask array
        --------------------------------------------------
        
        Arguments:
        ----------
        self    :       : 
        
        Return:
        ----------
        None    : None  :
        """
        
        ratio = self.nn/self.tile_size
        for i in range(ratio):
            for j in range(ratio):
                self.mask[i*self.tile_size:(i + 1)*self.tile_size, j*self.tile_size:(j + 1)*self.tile_size] = i*ratio + j

#------------------------------------------------------------------------------

    def changetile_size(self, new_tile_size):
        """
        Changes self.tile_size of the Grid_mask. Only proper divisors of self.nn will be accepted.
        mask array will be updated.
        --------------------------------------------------
        
        Arguments:
        ----------
        new_tile_size   : int   : dimensions of the tiles, which build up the grid
        
        Retrun:
        ----------
        None            : None  :
        """
        
        if self.nn % new_tile_size == 0:
            self.tile_size = new_tile_size
            self.create_grid_mask()
        else:
            print('tile_size is not a divisor of nn! Nothing will be updated.')

#------------------------------------------------------------------------------

    def show_Grid_mask(self):
        """
        Fast visualization of the Grid_mask.mask array
        --------------------------------------------------
        
        Arguments:
        ----------
        self    :       : 
        
        Return:
        ----------
        None    :       : 
        """
        
        temparr = where(self.mask %2 == 1, 1, -1)
        if (self.nn / self.tile_size) % 2 == 0:
            temparr = abs(temparr + temparr.T) - 1
        self.show_mask(temparr, self.masktype)

#------------------------------------------------------------------------------

    def _contract_data(self, data):
        """
        Contracts the data set by applying the grid of the mask.
        data.shape = (128,128) & mask.shape = (128,128) | mask.tile_size = 4 ==> contr_data.shape = (32,32)
        --------------------------------------------------
        
        Arguments:
        ----------
        data        : ndarray   : MIEZE data of shape (#xpixel, #ypixel)
        
        Return:
        ----------
        contr_data  : ndarray   : contracted (summed for each tile) of shape (#xpixel/tile_size, #ypixel/tile_size)
        """
        
        tiles_per_row = self.nn/self.tile_size
        contr_data = zeros(tiles_per_row*tiles_per_row)
        for i in range(tiles_per_row*tiles_per_row):
            mask_tile = where(self.mask == i, 1., 0.)
            contr_data[i] = nansum(mask_tile*data)
            
        return contr_data.reshape((tiles_per_row, tiles_per_row))

#------------------------------------------------------------------------------

    def _expand_data(self, data):
        """
        Expands data by if array dimensions fit to Grid_mask.
        data.shape = (128,128) & mask.shape = (256,256) | mask.tile_size = 2 ==> expa_data.shape = (256,256)
        --------------------------------------------------
        
        Arguments:
        ----------
        data        : ndarray   : MIEZE data of shape (#x, #y)
        
        Return:
        ----------
        expa_data  : ndarray   : expanded (copied the same value of smaller array to indices of a tile) data
                                 of shape (#x*tile_size, #y*tile_size)
        """
        
        tile_size = self.tile_size
        expa_data = zeros((self.nn,)*2)
        for i, row in enumerate(data):
            for j, el in enumerate(row):
                expa_data[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size] = el
            
        return expa_data


###############################################################################
###############################################################################

class Sector_Mask(Mask_Base):
    """
    Sector_Mask class masking data in a circular or sector shape
    """
    
    def __init__(self, nn, centre, inner_radius, outer_radius, angle_range, instrument):
        """
        Constructor of a Grid_mask objects.
        --------------------------------------------------
        
        Arguments:
        ----------
        nn              : int           : mask array with dimension nn x nn
        centre          : tuple         : indices of the beam center (center_xcoord, center_ycoord)
        inner_radius    : int           : inner radius of a circular mask in pixel
        outer_radius    : int           : outer radius of a circular mask in pixel
        angle_range     : tuple         : (start_angle, end_angle) in  clockwise sense in degrees, from 0 to 360,
                                          starting along the positive y-directio on the 2D panel.
        instrument      : str           : specifies the instrument to access Instrument parameter dictionary
                                          'MIRA', 'RESEDA', 'RESEDAlegacy'
        
        Return:
        ----------
        obj             : Sector_mask   : 
        """
        
        Mask_Base.__init__(self, nn, instrument)
        self.masktype = 'Sector mask'
        self.centre = centre
        self.r_i = inner_radius
        self.r_o = outer_radius
        self.tmin, self.tmax = deg2rad(angle_range)
        self.create_sector_mask()
        self.qxyz = zeros((self.nn, self.nn, 3))

#------------------------------------------------------------------------------

    def create_sector_mask(self):
        """
        Generates the array representation of the Sector_mask object.
        --------------------------------------------------
        
        Arguments:
        ----------
        self    :       : 
        
        Returns:
        ----------
        None    :       : 
        """

        y,x = ogrid[:self.nn,:self.nn]
        cx,cy = self.centre
        
        #ensure stop angle > start angle
        if self.tmax<self.tmin:
            self.tmax += 2*pi
        #convert cartesian --> polar coordinates
        r2 = (x-cx)*(x-cx) + (y-cy)*(y-cy)
        theta = arctan2(x-cx,y-cy) - self.tmin
        #wrap angles between 0 and 2*pi
        theta %= (2*pi)
        #circular mask
        circmask = r2 <= self.r_o*self.r_o
        circmask2 = r2 >= self.r_i*self.r_i
        # angular mask
        anglemask = theta <= (self.tmax-self.tmin)

        self.mask = circmask*circmask2*anglemask

#------------------------------------------------------------------------------
        
    def every_q(self):
        """
        Calculates the qx, qy, qz value of a neutron arriving at a certain detector pixel,
        considering the center of the mask to be the direct beam spot at on the detector.
        --------------------------------------------------
        
        Arguments:
        ----------
        self    :       : 
        
        Returns:
        ----------
        None    :       : 
        """

        cx, cy = self.centre
        qq = (2*pi/6.0)

        for x in range(cx - (self.r_o + 1), cx + (self.r_o + 2)):
            for y in range(cy - (self.r_o + 1), cy + (self.r_o + 2)):
                n_path_length = sqrt(self.d_SD**2 + self.pixelsize**2*(x-cx)**2 + self.pixelsize**2*(y-cy)**2)
                try:
                    self.qxyz[y,x,0] = self.pixelsize*(x-cx)/n_path_length * qq
                    self.qxyz[y,x,1] = self.pixelsize*(y-cy)/n_path_length * qq
                    self.qxyz[y,x,2] = (self.d_SD/n_path_length - 1) * qq
                    
                except IndexError:
                    pass

#------------------------------------------------------------------------------

    def q(self, counter = 0):
        """
        Calculates the average |q| value of a sector mask.
        --------------------------------------------------
        
        Arguments:
        ----------
        counter     : int   : counter to supress recalculation of all the momentum components
        
        Return:
        ----------
        q_abs       : float : absolute momentum transfer considering quasi elastic scattering
        q_abs_err   : float : error of the absolute momentum transfer
        """

        while counter < 2:
#            q_abs = np.sqrt(np.sum(self.qxyz**2, axis = 2)) * self.mask / self.mask.sum()
            q_abs = sum(sqrt(sum(self.qxyz**2, axis = 2)) * self.mask) / self.mask.sum()
            q_abs_err = sqrt(1.0/(self.mask.sum() - 1) * sum(((sqrt(sum(self.qxyz**2, axis = 2)) - q_abs) * self.mask)**2))
            if q_abs.any() != 0:
                return q_abs, q_abs_err
            else:
                self.every_q()
                self.q(counter + 1)

#------------------------------------------------------------------------------

    def show_sector_mask(self):
        """
        Fast visualization of the Sector_mask.mask array
        --------------------------------------------------
        
        Arguments:
        ----------
        self    :       : 
        
        Return:
        ----------
        None    :       : 
        """
        
        Mask_Base.show_mask(where(self.mask == True, 1, 0), self.masktype)

#------------------------------------------------------------------------------

    def _contract_data(self, data):
        """
        Contracts the data set by applying selecting data points according to the masks shape.
        --------------------------------------------------
        
        Arguments:
        ----------
        data        : ndarray       : MIEZE data of shape (#xpixel, #ypixel)
        
        Return:
        ----------
        contr_data  : int / float   : summed data points over the non masked values
        """
        
        return sum(data * self.mask)

#------------------------------------------------------------------------------

    def apply_mask(self, data, task = 'contract'):
        """
        Applies a given task to the supplied data.
        --------------------------------------------------
        
        Arguments:
        ----------
        data        : ndarray   : data array of the form: (n_1, n_2, ..., n_x, #xpixel, #ypixel)
        task        : str       : specifies task to perform with selected data points
                              'contract': sum over all points on the 2D detector
        
        Return:
        ----------
        proc_dat    : ndarray   : processed data of shape (n_1, n_2, ..., n_x, some_method(array*mask))
        """
        
        reshaped_data = data.reshape((-1,) + data.shape[-2:])
        for panelind, panel in enumerate(reshaped_data):
            if task == 'contract':
                reshaped_data[panelind] = self._contract_data(panel)
            elif task == 'cut':
                print("The 'cut' option has not been implemented, yet.")
            elif task == 'average':
                print("The 'average' option has not been implemented, yet.")
            else:
                print("The '{}' option is not known. Possible typo?".format(task))
        return reshaped_data.reshape(data.shape)


###############################################################################
###############################################################################

class Square_Mask(Mask_Base):
    """
    Square_Mask class masking data in a rectangular shape.
    """

    def __init__(self, nn, instrument, left, length, bottom, height, *args):
        """
        Constructor of a Square_mask objects.
        --------------------------------------------------
        
        Arguments:
        ----------
        nn              : int           : mask array with dimension nn x nn
        instrument      : str           : specifies the instrument to access Instrument parameter dictionary
                                          'MIRA', 'RESEDA', 'RESEDAlegacy'
        llbh            : tuple         : (left, length, bottom, height) in pixels
        args            : list          : [left2, length2, bottom2, height2, left3, ... heightn]
        
        Return:
        ----------
        obj             : Square_mask   : 
        """
        
        
        Mask_Base.__init__(self, nn, instrument)
        self.masktype = 'Square mask'
        
        self.lefts, self.lengths, self.bottoms, self.heights = [left], [length], [bottom], [height]
        if len(args) % 4 == 0 and len(args) != 0:
            for i, el in enumerate(args):
                if i % 4 == 2:
                    self.lefts.append(el)
                elif i % 4 == 3:
                    self.lengths.append(el)
                elif i % 4 == 0:
                    self.bottoms.append(el)
                elif i % 4 == 1:
                    self.heights.append(el)
        
        self.mask = self.mask.astype(bool)
        for llbhval in range(len(self.lefts)):
            self.mask[self.lefts[llbhval]:self.lefts[llbhval] + self.lengths[llbhval], self.bottoms[llbhval]:self.bottoms[llbhval] + self.heights[llbhval]] = True

#------------------------------------------------------------------------------

    def show_square_mask(self):
        """
        Fast visualization of the Square_mask.mask array
        --------------------------------------------------

        Arguments:
        ----------
        self    :       : 
        
        Return:
        ----------
        None    :       : 
        """

        self.show_mask(self.mask, self.masktype)

###############################################################################
###############################################################################

class Instrument:
    """
    Instrument class to store instrument related values (might need overhaul in the future)
    """

    RESEDA = {}
    MIRA = {}
    
    RESEDA['distance_SD'] = (2.25, 'm')
    RESEDA['distance_SD_err'] = (0.001,'m')     # 'm' meaning absolute error in the respective unit
    MIRA['distance_SD'] = (1.5, 'm')
    MIRA['distance_SD_err'] = (0.001,'m')
    
    RESEDA['wavelength'] = (6.0, 'A-1')
    RESEDA['wavelength_err'] = (10.0, 'rel')    # 'rel' meaning relative error in percent
    MIRA['wavelength'] = (4.33, 'A-1')
    MIRA['wavelength_err'] = (1.0, 'rel')
    
    RESEDA['foils'] = (7, 6, 5, 0, 1, 2)
    MIRA['foils'] = (0, 5, 6, 1)

#------------------------------------------------------------------------------

    @classmethod
    def get_Parameters(cls, mainkey, *subkeys):
        """
        Retrievs parameters of a specified instrument (At some point, catch sub- and mainkeys individually)
        
        Arguments:
        ----------
        mainkey     : str   : one of the Instruments 'MIRA', 'RESEDA'
        *subkeys    : list  : list of parameters to extract, 'wavelength' etc.
        
        Return:
        ----------
        retdict     : dict  : dictionary containing the parameters specified in the arguments
        """

        retdict = {}
        try:
            for subkey in subkeys:
                if mainkey == 'MIRA':
                    par = cls.MIRA[subkey]
                    try:
                        err = cls.MIRA['{}_err'.format(subkey)]
                        if err[1] != 'rel':
                            retdict[subkey] = (par[0], err[0], par[1])
                        else:
                            retdict[subkey] = (par[0], par[0] * err[0]/100.0, par[1])
                    except KeyError:
                        retdict[subkey] = par
                elif mainkey == 'RESEDA':
                    par = cls.RESEDA[subkey]
                    try:
                        err = cls.RESEDA['{}_err'.format(subkey)]
                        if err[1] != 'rel':
                            retdict[subkey] = (par[0], err[0], par[1])
                        else:
                            retdict[subkey] = (par[0], par[0] * err[0]/100.0, par[1])
                    except KeyError:
                        retdict[subkey] = par
        except KeyError:
            print('A key was not recognized. Check for typing error! Individual catches will be implemented later...')
        
        finally:
            return retdict

#------------------------------------------------------------------------------