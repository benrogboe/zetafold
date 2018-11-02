from alphafold.explicit_recursions import *

def get_random_contrib( contribs ):
    # Random sample weighted by probability. Must be a simple function for this.
    contrib_cumsum = [ contribs[0][0] ]
    for contrib in contribs[1:]: contrib_cumsum.append( contrib_cumsum[-1] + contrib[0] )
    r = random.random() * contrib_cumsum[ -1 ]
    for (idx,psum) in enumerate( contrib_cumsum ):
        if r < psum: return contribs[idx]

##################################################################################################
def backtrack( self, contribs_input, mode = 'mfe' ):
    if len( contribs_input ) == 0: return []
    #print 'contribs_input', contribs_input
    contrib_sum = sum( contrib[0] for contrib in contribs_input )
    if   mode == 'enumerative': contribs = deepcopy( contribs_input )
    elif mode == 'mfe':         contribs = [ max( contribs_input ) ]
    elif mode == 'stochastic' : contribs = [ get_random_contrib( contribs_input ) ]
    p_bps = [] # list of tuples of (p_structure, bps_structure) for each structure
    N = self.N
    for contrib in contribs: # each option ('contribution' to this partition function of this sub-region)
        if ( contrib[0] == 0.0 ): continue
        p_contrib = contrib[0]/contrib_sum
        p_bps_contrib = [ [p_contrib,[]] ]

        for backtrack_info in contrib[1]: # each 'branch'
            ( Z_backtrack_id, i, j )  = backtrack_info
            if Z_backtrack_id == self.Z_BP:
                update_Z_BP( self, i, j, calc_contrib = True )
                backtrack_contrib = self.Z_BP.contrib
                p_bps_contrib = [ [p_bp[0], p_bp[1]+[(i%N,j%N)] ] for p_bp in p_bps_contrib ]
            elif Z_backtrack_id == self.C_eff:
                update_C_eff( self, i, j, calc_contrib = True )
                backtrack_contrib = self.C_eff.contrib
            elif Z_backtrack_id == self.C_eff_no_coax_singlet:
                update_C_eff( self, i, j, calc_contrib = True )
                backtrack_contrib = self.C_eff_no_coax_singlet.contrib
            elif Z_backtrack_id == self.Z_linear:
                update_Z_linear( self, i, j, calc_contrib = True )
                backtrack_contrib = self.Z_linear.contrib
            p_bps_component = backtrack( self, backtrack_contrib[i%N][j%N], mode )
            if len( p_bps_component ) == 0: continue
            # put together all branches
            p_bps_contrib_new = []
            for p_bps1 in p_bps_contrib:
                for p_bps2 in p_bps_component:
                    p_bps_contrib_new.append( [p_bps1[0]*p_bps2[0], p_bps1[1]+p_bps2[1]] )
            p_bps_contrib = p_bps_contrib_new

        p_bps += p_bps_contrib
    return p_bps

##################################################################################################
def mfe( self, Z_final_contrib ):
    p_bps = backtrack( self, Z_final_contrib, mode = 'mfe' )
    assert( len(p_bps) == 1 )
    return (p_bps[0][1],p_bps[0][0])

##################################################################################################
def boltzmann_sample( self, Z_final_contrib ):
    p_bps = backtrack( self, Z_final_contrib, mode = 'stochastic' )
    assert( len(p_bps) == 1 )
    return (p_bps[0][1],p_bps[0][0])
