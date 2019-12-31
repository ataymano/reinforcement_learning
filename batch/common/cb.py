class CB:
    @staticmethod
    def get_label(vw_ex):
        if vw_ex.get_cbandits_num_costs() > 0:
            return [vw_ex.get_cbandits_cost(0), vw_ex.get_cbandits_probability(0)]
        return []