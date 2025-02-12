""" Common utilities for reaction classes
"""
import automol.graph
from automol.graph import ts
from automol import par


def hydrogen_migration_atom_keys(rxn):
    """ Obtain the atoms involved in a hydrogen migration reaction, sorted in
    canonical order.

    :param rxn: the reaction object
    :type rxn: Reaction
    :returns: the attacking atom, the transferring atom, the donating atom, and
    a neighbor to the attacking atom along the chain to the donating atom
    :rtype: (int, int, int, int)
    """
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    tra_key, = frm_bnd_key & brk_bnd_key
    att_key, = frm_bnd_key - brk_bnd_key
    don_key, = brk_bnd_key - frm_bnd_key

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    path = automol.graph.shortest_path_between_atoms(gra, att_key, don_key)
    ngb_key = automol.graph.atom_neighbor_atom_key(
        gra, att_key, incl_atm_keys=path)
    return att_key, tra_key, don_key, ngb_key


def ring_forming_scission_atom_keys(rxn):
    """ Obtain the atoms involved in a ring-forming scission reaction, sorted in
    canonical order.

    :param rxn: the reaction object
    :type rxn: Reaction
    :returns: the attacking atom, the transferring atom, the donating atom
    :rtype: (int, int, int, int)
    """
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    tra_key, = frm_bnd_key & brk_bnd_key
    att_key, = frm_bnd_key - brk_bnd_key
    don_key, = brk_bnd_key - frm_bnd_key
    return att_key, tra_key, don_key


def ring_forming_scission_chain(rxn):
    """ Obtain the chain in a ring-forming scission reaction from the donating
    attom to the attacking atom.

    :param rxn: the reaction object
    :type rxn: Reaction
    :returns: atoms along the chain
    :rtype: tuple[int]
    """
    att_key, _, don_key = ring_forming_scission_atom_keys(rxn)
    gra = ts.reactants_graph(rxn.forward_ts_graph)
    path = automol.graph.shortest_path_between_atoms(gra, don_key, att_key)
    return tuple(path)


def hydrogen_abstraction_atom_keys(rxn):
    """ Obtain the atoms involved in a hydrogen abstraction, sorted in
    canonical order.

    :param rxn: the reaction object
    :type rxn: Reaction
    :returns: the attacking atom, the transferring atom, the donating atom
    :rtype: (int, int, int)
    """
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    hyd_key, = frm_bnd_key & brk_bnd_key
    att_key, = frm_bnd_key - brk_bnd_key
    don_key, = brk_bnd_key - frm_bnd_key
    return att_key, hyd_key, don_key


def hydrogen_abstraction_is_sigma(rxn):
    """ Is this a sigma radical hydrogen abstraction?

    :param rxn: the reaction object
    :type rxn: Reaction
    :rtype: bool
    """
    assert rxn.class_ == par.ReactionClass.HYDROGEN_ABSTRACTION
    tsg = rxn.forward_ts_graph
    rct_gra = automol.graph.ts.reactants_graph(tsg)
    sig_rad_keys = automol.graph.sigma_radical_atom_keys(rct_gra)

    brk_bnd_key, = ts.breaking_bond_keys(tsg)
    frm_bnd_key, = ts.forming_bond_keys(tsg)
    rad_key, = frm_bnd_key - brk_bnd_key
    return rad_key in sig_rad_keys


def insertion_forming_bond_keys(rxn):
    """ Obtain the forming bonds for an insertion reaction, sorted in canonical
    order.

    :param rxn: the reaction object
    :type rxn: Reaction
    :returns: the forming bond keys
    :rtype: (frozenset[int], frozenset[int])
    """
    assert rxn.class_ == par.ReactionClass.INSERTION
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    # Choose the forming bond that doesn't intersect with the breaking bond, if
    # one of them does
    frm_bnd_keys = sorted(ts.forming_bond_keys(rxn.forward_ts_graph),
                          key=sorted)
    frm_bnd_keys = sorted(frm_bnd_keys,
                          key=lambda x: len(x & brk_bnd_key))
    return tuple(frm_bnd_keys)


def substitution_atom_keys(rxn):
    """ Obtain the atoms involved in a substitution reaction, sorted in
        canonical order.

    :param rxn: the reaction object
    :type rxn: Reaction
    :returns: the attacking atom, the transferring atom, the leaving atom
    :rtype: (int, int, int)
    """
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    tra_key, = frm_bnd_key & brk_bnd_key
    att_key, = frm_bnd_key - brk_bnd_key
    lea_key, = brk_bnd_key - frm_bnd_key
    return att_key, tra_key, lea_key


# Get a reaction object from various identifiers
def rxn_objs_from_inchi(rct_ichs, prd_ichs, indexing='geo'):
    """ Generate obj
    """

    rct_geos = list(map(automol.inchi.geometry, rct_ichs))
    prd_geos = list(map(automol.inchi.geometry, prd_ichs))

    return rxn_objs_from_geometry(
        rct_geos, prd_geos, indexing=indexing)


def rxn_objs_from_smiles(rct_smis, prd_smis, indexing='geo'):
    """ Generate obj
    """

    # Is this adding stero? prob should?
    rct_ichs = list(map(automol.smiles.inchi, rct_smis))
    prd_ichs = list(map(automol.smiles.inchi, prd_smis))

    rct_geos = list(map(automol.inchi.geometry, rct_ichs))
    prd_geos = list(map(automol.inchi.geometry, prd_ichs))

    return rxn_objs_from_geometry(
        rct_geos, prd_geos, indexing=indexing)


def rxn_objs_from_zmatrix(rct_zmas, prd_zmas, indexing='geo'):
    """ Generate rxn obj
    """

    rct_geos = list(map(automol.zmat.geometry, rct_zmas))
    prd_geos = list(map(automol.zmat.geometry, prd_zmas))

    return rxn_objs_from_geometry(
        rct_geos, prd_geos, indexing=indexing)


def rxn_objs_from_geometry(rct_geos, prd_geos, indexing='geo'):
    """ from
    """

    # Identify the reaction based on the reactants and products
    rct_gras = list(map(automol.graph.without_stereo_parities,
                        map(automol.geom.graph, rct_geos)))
    prd_gras = list(map(automol.graph.without_stereo_parities,
                        map(automol.geom.graph, prd_geos)))

    rct_gras, _ = automol.graph.standard_keys_for_sequence(rct_gras)
    prd_gras, _ = automol.graph.standard_keys_for_sequence(prd_gras)

    rxns = automol.reac.find(rct_gras, prd_gras)

    # Obtain the reaction objects and structures to return
    rxn_objs = tuple()
    for rxn in rxns:
        std_rxn, std_rgeos, std_pgeos = (
            automol.reac.standard_keys_with_sorted_geometries(
                rxn, rct_geos, prd_geos))
        ts_geo = automol.reac.ts_geometry(std_rxn, std_rgeos, log=False)

        # Determine which geometries to store
        if indexing == 'geo':
            rxn_objs += ((std_rxn, ts_geo, std_rgeos, std_pgeos),)
        elif indexing == 'zma':
            ts_zma, zma_keys, dummy_key_dct = automol.reac.ts_zmatrix(
                std_rxn, ts_geo)
            std_zrxn = automol.reac.relabel_for_zmatrix(
                std_rxn, zma_keys, dummy_key_dct)
            rct_zmas = tuple(map(automol.geom.zmatrix, rct_geos))
            prd_zmas = tuple(map(automol.geom.zmatrix, prd_geos))

            rxn_objs += ((std_zrxn, ts_zma, rct_zmas, prd_zmas),)

    return rxn_objs


if __name__ == '__main__':
    rct_ichs, prd_ichs = [
        ['InChI=1S/C7H14/c1-6(2)5-7(3)4/h7H,1,5H2,2-4H3',
         'InChI=1S/CH3/h1H3'],
        ['InChI=1S/C8H17/c1-7(2)6-8(3,4)5/h7H,3,6H2,1-2,4-5H3']]
    rxn_objs_from_inchi(rct_ichs, prd_ichs)
