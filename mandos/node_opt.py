import math
from scipy import optimize
import tree_reader2
import tree_utils2
import calc_bm_likelihood
import random
import sys
import numpy as np
LARGE = 100000000000


def bm_sigsq_optim(tree,traits,rate=1):
    # tree_utils2.assign_sigsq(tree,[rate])
    start = [rate]
    opt = optimize.fmin_powell(calc_like_sigsq, start, args = (tree,traits),full_output=False,disp=True)
    return [tree.get_newick_repr(True),opt]


def calc_like_sigsq(sigsq,tree,traits):
    if sigsq < 0:
        return LARGE
    #tree_utils2.assign_sigsq(tree,sigsq)
    try:
        val = -calc_bm_likelihood.bm_prune(tree,traits,sigsq)
    except:
        return LARGE
    #print ht,val
    return val


def bm_brlen_optim(tree,ntraits,method="bfgs",sigsq = 1.):
    #tree_utils2.assign_branch_nums(tree)
    #start = np.array([i.length for i in tree.iternodes() if i != tree],dtype=np.double)
    #start = np.array([1.0 for i in tree.iternodes() if i != tree],dtype=np.double)
    start = []
    fixed_tip = True
    for node in tree.iternodes():
        if node == tree:
            continue
        elif node.istip == True and fixed_tip == True:
            node.length = 1.0
            fixed_tip = False
            continue
        start.append(1.0)
    start = np.array(start,dtype=np.double)
    opt = optimize.minimize(calc_like_brlens, start, args = (tree,ntraits,sigsq),method="Powell")
    #print opt.x
    #print tree.get_newick_repr(True)
    count = 0
    fixed_tip = True
    for node in tree.iternodes():
        if node == tree:
            continue
        elif node.istip == True and fixed_tip == True:
            fixed_tip = False
            continue
        node.length = opt.x[count]
        count += 1
    return [tree.get_newick_repr(True),opt]


def fix_bad_brlens(node):
    for i in node.iternodes():
        if i.length < 0.001:
            i.length = 0.1

def calc_like_sigsq_brlens(l,tree,ntraits):
    bad = tree.update_brlens_all(l[1:])
    #bad = tree_utils2.assign_brlens(l,tree)
    if bad:
        return LARGE
    elif l[0] < 0:
        return LARGE
    try:
        ll = -calc_bm_likelihood.bm_prune(tree,ntraits,l[0])
    except:
        return LARGE
    return ll

def calc_like_brlens(l,tree,ntraits,sigsq = 1.):
    bad = tree.update_brlens_all(l)
    #bad = tree_utils2.assign_brlens(l,tree)
    if bad:
        return LARGE
    try:
        ll = -calc_bm_likelihood.bm_prune(tree,ntraits,sigsq)
    except:
        return LARGE
    return ll

def calc_like_single_brlen(bl,node,tree,ntraits,sigsq=1.):
    #if bl[0] < 0.00001:
    #    return LARGE
    bad = node.update_child_brlens(bl)
    if bad:
        return LARGE
    try:
        ll = -calc_bm_likelihood.bm_prune(tree,ntraits,sigsq)
    except:
        return LARGE
    return ll

def calc_like_single_conditional_brlen(bl,node,tree,ntraits,sigsq=1.):
    #if bl[0] < 0.00001:
    #    return LARGE
    bad = node.update_child_brlens(bl)
    if bad:
        return LARGE
    try:
        ll = -calc_bm_likelihood.bm_prune(tree,ntraits,sigsq)
    except:
        return LARGE
    return ll

def bm_single_brlen_optim(tree,ntraits,sigsq=1.,alg="Powell"):
    count = 0
    for node in tree.iternodes(order=1):
        if node.istip:
            #count += 1
            continue
        start = np.array([child.length for child in node.children],dtype=np.double)
        if alg == "Powell": 
            opt = optimize.minimize(calc_like_single_brlen,start,args=(node,tree,ntraits,sigsq), method = "Powell")
        elif alg == "SLSQP":
            opt = optimize.minimize(calc_like_single_brlen,start,args=(node,tree,ntraits,sigsq), method = "SLSQP",bounds=((0.00001,1000.),(0.00001,1000.)))
        elif alg == "L-BFGS-B":
            opt = optimize.minimize(calc_like_single_brlen,start,args=(node,tree,ntraits,sigsq), method = "L-BFGS-B",bounds=((0.00001,1000.),(0.00001,1000.)))

        #print opt.x
        ccount = 0
        for child in node.children:
            child.length = opt.x[ccount]
            ccount+=1
        count += 1
    return [tree.get_newick_repr(True),opt]


