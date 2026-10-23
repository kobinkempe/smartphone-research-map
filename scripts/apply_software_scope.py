"""Apply the user's software black-box clarification through the atomic gate."""
import copy
import json
from pathlib import Path
from graph_gate import load_json, apply_proposal

ROOT=Path(__file__).resolve().parents[1]
SOFTWARE={'boot-tools','design-tools','test-software','firmware-build-tools','firmware',
          'operating-system','offline-apps','protocol-stack'}

def main():
    current=load_json(ROOT/'data/registry.json')
    if all(n.get('scope')=='black-box-software' for n in current['nodes'] if n['id'] in SOFTWARE):
        print('Software allowance already applied');return
    updates=[]
    physical_names={'bootstrap-computer':'Workshop computer','process-control':'Process controller',
                    'software-provisioning':'Programming fixture','boot-and-development-tools':'Programming tools'}
    for node in current['nodes']:
        if node['id'] in SOFTWARE:
            node=copy.deepcopy(node)
            node.update(scope='black-box-software',research_status='black-box',
                        summary=node['summary']+' Software implementation is outside manufacturing research under the user\'s black-box allowance.',
                        software_boundary={'implementation':'black-box','availability':'Record the required stage; finished-phone installation may occur after real-world import.'})
            updates.append(node)
        elif node['id'] in physical_names:
            node=copy.deepcopy(node)
            node.update(name=physical_names[node['id']],scope='physical',
                        summary='Physical '+physical_names[node['id']].lower()+' hardware. Compatible black-box software functions and availability timing must be specified; no software implementation research is required.')
            updates.append(node)
    proposal={'base_revision':current['revision'],'proposal_id':'software-black-box-scope',
              'author':'coordinator','reason':'Explicit user clarification: research physical product, treat software as a black box.',
              'upsert_nodes':updates}
    folder=ROOT/'proposals';folder.mkdir(exist_ok=True)
    (folder/'software-black-box-scope.json').write_text(json.dumps(proposal,indent=2)+'\n',encoding='utf-8')
    report=apply_proposal(ROOT/'data/registry.json',proposal)
    print(json.dumps({'revision':report['revision'],'black_box_software_records':len(SOFTWARE),'updated_nodes':len(updates)}))

if __name__=='__main__':main()
