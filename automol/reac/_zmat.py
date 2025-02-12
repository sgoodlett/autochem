""" TS z-matrices for specific reaction classes
"""
import automol.geom
import automol.graph
from automol import par
from automol.graph import ts
from automol.reac._reac import add_dummy_atoms
from automol.reac._util import hydrogen_migration_atom_keys
from automol.reac._util import ring_forming_scission_atom_keys
from automol.reac._util import insertion_forming_bond_keys
from automol.reac._util import hydrogen_abstraction_atom_keys
from automol.reac._util import hydrogen_abstraction_is_sigma
from automol.reac._util import substitution_atom_keys


# Unimolecular reactions
# 1. Hydrogen migrations
def hydrogen_migration_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for a hydrogen migration transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    # Start the z-matrix from the forming bond ring
    rng_keys, = ts.forming_rings_atom_keys(rxn.forward_ts_graph)
    _, hyd_key, don_key, _ = hydrogen_migration_atom_keys(rxn)
    # Cycle the migrating h to the front of the ring keys and, if
    # needed, reverse the ring so that the donating atom is last:
    #       (migrating h atom, attacking atom, ... , donating atom)
    # This ensures that the forming bond coordinate is included in the z-matrix
    # and drops the breaking bond coordinate from the z-matrix.
    rng_keys = automol.graph.cycle_ring_atom_key_to_front(
        rng_keys, hyd_key, end_key=don_key)
    vma, zma_keys = automol.graph.vmat.vmatrix(
        rxn.forward_ts_graph, rng_keys=rng_keys)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# 2. Beta scissions
def beta_scission_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for a beta scission transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    vma, zma_keys = automol.graph.vmat.vmatrix(rxn.forward_ts_graph)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# 3. Ring-forming scissions
def ring_forming_scission_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for a ring-forming scission transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    rng_keys, = ts.forming_rings_atom_keys(rxn.forward_ts_graph)
    att_key, tra_key, _ = ring_forming_scission_atom_keys(rxn)
    # First, cycle the transferring atom to the front of the ring keys and, if
    # needed, reverse the ring so that the attacking atom is last
    #       (transferring atom, ... , atom, attackin atom)
    rng_keys = automol.graph.cycle_ring_atom_key_to_front(
        rng_keys, tra_key, end_key=att_key)
    # Now, cycle the secont-to-last key to the front so that the ring order is:
    #       (atom, attacking atom, transferring atom, ....)
    rng_keys = automol.graph.cycle_ring_atom_key_to_front(
        rng_keys, rng_keys[-2])
    vma, zma_keys = automol.graph.vmat.vmatrix(rxn.forward_ts_graph)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# 4. Eliminations
def elimination_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for an elimination transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    rng_keys, = ts.forming_rings_atom_keys(rxn.forward_ts_graph)
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    # Drop one of the breaking bonds from the z-matrix by sorting the ring atom
    # keys to exclude it. If one of the breaking bonds intersects with the
    # forming bond, choose the other one.
    brk_bnd_keys = sorted(ts.breaking_bond_keys(rxn.forward_ts_graph),
                          key=lambda x: len(x & frm_bnd_key))
    brk_bnd_key = brk_bnd_keys[0]
    # Cycle the ring keys such that the atom closest to the forming bond is the
    # beginning of the ring and the other atom is the end
    if brk_bnd_key & frm_bnd_key:
        key1, = brk_bnd_key & frm_bnd_key
        key2, = brk_bnd_key - frm_bnd_key
    else:
        path = automol.graph.shortest_path_between_groups(
            rxn.forward_ts_graph, brk_bnd_key, frm_bnd_key)
        key1, = brk_bnd_key & set(path)
        key2, = brk_bnd_key - set(path)
    rng_keys = automol.graph.cycle_ring_atom_key_to_front(
        rng_keys, key1, end_key=key2)

    vma, zma_keys = automol.graph.vmat.vmatrix(
        rxn.forward_ts_graph, rng_keys=rng_keys)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# Bimolecular reactions
# 1. Hydrogen abstractions
def hydrogen_abstraction_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for a hydrogen abstraction transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))
    # Add a dummy atom over the transferring hydrogen
    att_key, hyd_key, _ = hydrogen_abstraction_atom_keys(rxn)
    lin_idxs.append(hyd_key)

    if hydrogen_abstraction_is_sigma(rxn):
        if att_key not in lin_idxs:
            lin_idxs.append(att_key)

    lin_idxs = sorted(lin_idxs)

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    tsg = rxn.forward_ts_graph
    rct1_keys, rct2_keys = rxn.reactants_keys
    vma, zma_keys = automol.graph.vmat.vmatrix(tsg, rct1_keys)
    vma, zma_keys = automol.graph.vmat.continue_vmatrix(
        tsg, rct2_keys, vma, zma_keys)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# 2. Additions
def addition_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for an addition transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()
    rxn.forward_ts_graph = rxn.forward_ts_graph

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    tsg = rxn.forward_ts_graph
    rct1_keys, rct2_keys = rxn.reactants_keys
    vma, zma_keys = automol.graph.vmat.vmatrix(tsg, rct1_keys)
    vma, zma_keys = automol.graph.vmat.continue_vmatrix(
        tsg, rct2_keys, vma, zma_keys)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# 3. Insertions
def insertion_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for an insertion transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()
    rxn.forward_ts_graph = rxn.forward_ts_graph

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    rng_keys, = ts.forming_rings_atom_keys(rxn.forward_ts_graph)
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    # Drop one of the forming bonds from the z-matrix by sorting the ring atom
    # keys to exclude it. If one of the forming bonds intersects with the
    # breaking bond, choose that one.
    _, frm_bnd_key = insertion_forming_bond_keys(rxn)
    # Cycle the ring keys such that the atom closest to the breaking bond is
    # the beginning of the ring and the other atom is the end
    if frm_bnd_key & brk_bnd_key:
        key1, = frm_bnd_key & brk_bnd_key
        key2, = frm_bnd_key - brk_bnd_key
    else:
        path = automol.graph.shortest_path_between_groups(
            rxn.forward_ts_graph, frm_bnd_key, brk_bnd_key)
        key2, = frm_bnd_key - set(path)
    rng_keys = automol.graph.cycle_ring_atom_key_to_front(
        rng_keys, key1, end_key=key2)

    vma, zma_keys = automol.graph.vmat.vmatrix(
        rxn.forward_ts_graph, rng_keys=rng_keys)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


# 4. Substitutions
def substitution_ts_zmatrix(rxn, ts_geo):
    """ z-matrix for a substitution transition state geometry

    :param rxn: a Reaction object
    :param ts_geo: a transition state geometry
    """
    rxn = rxn.copy()
    rxn.forward_ts_graph = rxn.forward_ts_graph

    # 1. Get keys to linear or near-linear atoms
    lin_idxs = list(automol.geom.linear_atoms(ts_geo))
    # Add a dummy atom over the transferring hydrogen
    _, tra_key, _ = substitution_atom_keys(rxn)
    lin_idxs.append(tra_key)

    # 2. Add dummy atoms over the linear atoms
    rcts_gra = ts.reactants_graph(rxn.forward_ts_graph)
    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(
        ts_geo, lin_idxs=lin_idxs, gra=rcts_gra)

    # 3. Add dummy atoms to the Reaction object as well
    rxn = add_dummy_atoms(rxn, dummy_key_dct)

    # 4. Generate a z-matrix for the geometry
    tsg = rxn.forward_ts_graph
    rct1_keys, rct2_keys = rxn.reactants_keys
    vma, zma_keys = automol.graph.vmat.vmatrix(tsg, rct1_keys)
    vma, zma_keys = automol.graph.vmat.continue_vmatrix(
        tsg, rct2_keys, vma, zma_keys)

    zma_geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, zma_geo)

    return zma, zma_keys, dummy_key_dct


def ts_zmatrix(rxn, ts_geo):
    """ reaction-class-specific embedding info

    :param rxn: a hydrogen migration Reaction object
    :param ts_geo: the TS geometry
    :returns: the TS z-matrix, the row keys, and the dummy index dictionary
    """
    function_dct = {
        # unimolecular
        par.ReactionClass.HYDROGEN_MIGRATION: hydrogen_migration_ts_zmatrix,
        par.ReactionClass.BETA_SCISSION: beta_scission_ts_zmatrix,
        par.ReactionClass.RING_FORM_SCISSION: ring_forming_scission_ts_zmatrix,
        par.ReactionClass.ELIMINATION: elimination_ts_zmatrix,
        # bimolecular
        par.ReactionClass.HYDROGEN_ABSTRACTION:
        hydrogen_abstraction_ts_zmatrix,
        par.ReactionClass.ADDITION: addition_ts_zmatrix,
        par.ReactionClass.INSERTION: insertion_ts_zmatrix,
        par.ReactionClass.SUBSTITUTION: substitution_ts_zmatrix,
    }

    fun_ = function_dct[rxn.class_]
    ret = fun_(rxn, ts_geo)
    return ret
