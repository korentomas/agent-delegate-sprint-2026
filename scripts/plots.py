"""Publication figures. No inference intervals for an exhaustive deterministic suite."""
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('results',type=Path);a=p.parse_args()
rows=list(csv.DictReader((a.results/'summary.csv').open()))
raw=list(csv.DictReader((a.results/'runs.csv').open()))
out=a.results/'figures';out.mkdir(exist_ok=True)
labels={'monitor':'External monitor','critic':'Visible critic','delegate':'Protected delegate','layered':'Layered control','matched_monitor':'Matched monitor','gates_only':'Gates only'}
colors={'monitor':'#54667a','critic':'#d48125','delegate':'#236db4','layered':'#098977','matched_monitor':'#ad467d','gates_only':'#6f8b42'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
fig,ax=plt.subplots(figsize=(8,4.6))
for c in labels:
 r=[x for x in rows if x['condition']==c]
 ax.plot([int(x['latency']) for x in r],[int(x['harm']) for x in r],label=labels[c],color=colors[c],marker='o' if c!='matched_monitor' else 'x',linestyle='--' if c in ['matched_monitor','gates_only'] else '-',linewidth=2)
ax.set(xlabel='Configured human response delay (simulation ticks)',ylabel='Executed harmful mock actions (sum across 8 fixtures)',xticks=[0,2,6],title='The channel helps; a representative adds no benefit in this model')
ax.legend(ncol=2,fontsize=8);ax.grid(alpha=.15)
fig.text(.06,.01,'Fixed scripted policies. Main slice: no capture, minority bypass enabled, complete mediation. No LLM trials.',fontsize=8)
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'latency.png');fig.savefig(out/'latency.pdf');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(9,4.5))
cs=['monitor','critic','delegate','layered','matched_monitor','gates_only'];r={x['condition']:x for x in rows if x['latency']=='6'}
for ax,field,title in [(axes[0],'correct_answers','Correct mock answers'),(axes[1],'false_pauses','Benign runs with a pause (out of 3)')]:
 ax.bar(range(len(cs)),[int(r[c][field]) for c in cs],color=[colors[c] for c in cs]);ax.set_xticks(range(len(cs)),[labels[c] for c in cs],rotation=45,ha='right',fontsize=8);ax.set_title(title,fontsize=11)
fig.suptitle('Containment has an availability cost (delay = 6 ticks)')
fig.text(.04,.015,'Counts describe eight designed fixtures, not estimates of real-world frequency. Answers use a toy sum task.',fontsize=8)
fig.tight_layout(rect=[0,.05,1,.94]);fig.savefig(out/'tradeoffs.png');fig.savefig(out/'tradeoffs.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.6))
scenarios=['minority_warning','hidden_violation'];names=['Captured; no bypass','Captured; bypass','Bypass; hidden gate gap']
mat=[]
for sc in scenarios:
 vals=[]
 for bp,cov in [('False','complete'),('True','complete'),('True','missing_hidden')]:
  x=next(x for x in raw if x['scenario']==sc and x['condition']=='delegate' and x['latency']=='6' and x['capture']=='True' and x['bypass']==bp and x['gate_coverage']==cov)
  vals.append(int(x['executed_harm']))
 mat.append(vals)
ax.imshow(mat,cmap='YlOrRd',vmin=0,vmax=3,aspect='auto');ax.set_xticks(range(3),names,fontsize=9);ax.set_yticks(range(2),['Visible violation','Hidden violation']);ax.set_title('Fault injection: reports cannot repair missing enforcement')
for i,row in enumerate(mat):
 for j,v in enumerate(row):ax.text(j,i,str(v),ha='center',va='center',fontsize=20,color='white' if v else 'black')
fig.text(.05,.01,'Cells: executed harmful actions. Protected delegate, delay 6. Capture and coverage are injected assumptions.',fontsize=8)
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'faults.png');fig.savefig(out/'faults.pdf');plt.close(fig)
print(out)
