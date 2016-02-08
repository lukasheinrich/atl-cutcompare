import os
import yaml
def collect_results(comp_id):
    result_files = ['comparisons/{}/{}.output.yaml'.format(comp_id,x) for x in ['lhs','rhs']]
    if not all([os.path.exists(x) for x in result_files]):
        return None
    lhs_results = yaml.load(open(result_files[0]))
    rhs_results = yaml.load(open(result_files[1]))
    results = [{'name':r['name'],'rhs':r['value'],'lhs':l['value']} for l,r in zip(lhs_results,rhs_results)]
    return results
