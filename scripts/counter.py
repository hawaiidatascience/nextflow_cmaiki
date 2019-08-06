import pandas as pd
from os.path import basename,splitext
import re

def guess_file_extension(files):
    extensions = { f.split(".")[-1] for f in files }

    if 'shared' in extensions:
        return ".shared"
    else:
        return ".count_table"
    
def get_file_extension(filename):
    splits = filename.split(".")

    if splits[-1]=='gz':
        return "{}.{}".format(*splits[-2:])
    return splits[-1]

class SequenceCounter:

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
        self.extension = None
        self.step_nb = float(self.name.split('-')[0])
        self.extension = path.split('.')[-1]
        
    def run(self,sample_names=None):
        if self.extension in ["shared","count_table","csv","tsv"]:
            counts = self.countTable(self.path)
            summary_df = counts.reindex(sample_names).fillna(0)
            
            return summary_df 
        else:
            return pd.Series([])
            
    def countTable(self,filename):
        name = self.name

        try:
            id_threshold = float(re.findall(r"\d[.]*[\d]*",
                                            splitext(basename(filename))[0])[0])
            name = "{0}_{1:d}".format(self.name,int(id_threshold))
        except:
            id_threshold = ""
                    
        if self.extension == "shared":
            table = pd.read_csv(filename, index_col="Group", sep='\t').drop(["label","numOtus"],axis=1).T
        elif self.extension == "count_table":
            table = pd.read_csv(filename, index_col=0, sep="\t").drop("total",axis=1)
        elif self.extension == "csv":
            table = pd.read_csv(filename,index_col=0)
        elif self.extension == "tsv":
            table = pd.read_csv(filename,index_col=0,sep='\t')
        else:
            print("Wrong extension (neither .shared or .count_table): {}".format(self.extension))

        summary = table.agg(lambda x: "{} ({} uniques)".format(x.sum(),(x>0).sum()))
        summary.index = summary.index.astype(str)
                
        return summary.rename(name)