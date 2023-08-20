import pandas as pd
from statsmodels.formula.api import logit

def model_process(model,formula):
  #formula='삶의사다리점수_변형~건강만족도+가족의수입만족도+주거환경만족도+가족관계만족도+직업만족도+사회적친분관계만족도+여가생활만족도'
  test_df=model.pvalues.to_frame()
  if any(test_df>0.05):
    if formula[formula.find(test_df.sort_values(by=0,ascending=False).index[0])-1]=="~":
      formula=formula.replace(test_df.sort_values(by=0,ascending=False).index[0],"")
    else:
      formula=formula.replace("+"+test_df.sort_values(by=0,ascending=False).index[0],"")
    return formula
  else:
    return False

def lgt(data,구분컬럼명=None):
  model={}
  if 구분컬럼명:
    for i in data[구분컬럼명].unique():
      use_df=data[data[구분컬럼명]==i]
      use_col=[x for x in data.columns if x.find("만족도")!=-1]
      use_col.append("삶의 사다리 점수")
      use_col2=list(map(lambda x:x.split(")")[-1].replace(" ",""),use_col))
      use_df.rename(columns=dict(zip(use_col,use_col2)),inplace=True)
      use_df=use_df[use_col2]
      # 중상위 결과
      use_df["삶의사다리점수_변형"]=use_df["삶의사다리점수"].apply(lambda x:1 if x>use_df["삶의사다리점수"].mean() else 0)
      formula=f'삶의사다리점수_변형~{"+".join(use_df.columns[:-2])}'
      result1=logit(formula,data=use_df).fit()
      while bool(model_process(formula,result1)):
        formula=model_process(formula,result1)
        result1=logit(formula,data=use_df).fit() 
      #print(result.summary(),"\n","정확도 :",(result.pred_table()[0,0]+result.pred_table()[1,1])/result.pred_table().sum())
      #최상위 결과
      top_df=use_df[use_df["삶의사다리점수_변형"]==1]
      top_df["삶의사다리점수_변형"]=top_df["삶의사다리점수"].apply(lambda x:1 if x>top_df["삶의사다리점수"].mean() else 0)
      formula=f'삶의사다리점수_변형~{"+".join(use_df.columns[:-2])}'
      result2=logit(formula,data=top_df).fit()
      while bool(model_process(formula,result2)):
        formula=model_process(formula,result2)
        result2=logit(formula,data=top_df).fit()  
      #최하위 결과
      low_df=use_df[use_df["삶의사다리점수_변형"]==0]
      low_df["삶의사다리점수_변형"]=low_df["삶의사다리점수"].apply(lambda x:1 if x>low_df["삶의사다리점수"].mean() else 0)
      formula=f'삶의사다리점수_변형~{"+".join(use_df.columns[:-2])}'
      result3=logit(formula,data=low_df).fit()
      while bool(model_process(formula,result3)):
        formula=model_process(formula,result3)
        result3=logit(formula,data=low_df).fit()
      ana_dc={"중상위":result1,"최상위":result2,"최하위":result3}
      model[i]=ana_dc
  else:
    use_df=data.copy()
    use_col=[x for x in data.columns if x.find("만족도")!=-1]
    use_col.append("삶의 사다리 점수")
    use_col2=list(map(lambda x:x.split(")")[-1].replace(" ",""),use_col))
    use_df.rename(columns=dict(zip(use_col,use_col2)),inplace=True)
    use_df=use_df[use_col2]
    # 중상위 결과
    use_df["삶의사다리점수_변형"]=use_df["삶의사다리점수"].apply(lambda x:1 if x>use_df["삶의사다리점수"].mean() else 0)
    formula=f'삶의사다리점수_변형~{"+".join(use_df.columns[:-2])}'
    result1=logit(formula,data=use_df).fit()
    while bool(model_process(formula,result1)):
      formula=model_process(formula,result1)
      result1=logit(formula,data=use_df).fit()
    #print(result.summary(),"\n","정확도 :",(result.pred_table()[0,0]+result.pred_table()[1,1])/result.pred_table().sum())
    #최상위 결과
    top_df=use_df[use_df["삶의사다리점수_변형"]==1]
    top_df["삶의사다리점수_변형"]=top_df["삶의사다리점수"].apply(lambda x:1 if x>top_df["삶의사다리점수"].mean() else 0)
    formula=f'삶의사다리점수_변형~{"+".join(use_df.columns[:-2])}'
    result2=logit(formula,data=top_df).fit()
    while bool(model_process(formula,result1)):
      formula=model_process(formula,result2)
      result2=logit(formula,data=top_df).fit() 
    #최하위 결과
    low_df=use_df[use_df["삶의사다리점수_변형"]==0]
    low_df["삶의사다리점수_변형"]=low_df["삶의사다리점수"].apply(lambda x:1 if x>low_df["삶의사다리점수"].mean() else 0)
    formula=f'삶의사다리점수_변형~{"+".join(use_df.columns[:-2])}'
    result3=logit(formula,data=low_df).fit()
    while bool(model_process(formula,result3)):
      formula=model_process(formula,result3)
      result3=logit(formula,data=low_df).fit()
    ana_dc={"중상위":result1,"최상위":result2,"최하위":result3}
    return ana_dc
  return model

def aucc(model):
  return (model.pred_table()[0,0]+model.pred_table()[1,1])/model.pred_table().sum()

def model_process(formula,model):
  #formula='삶의사다리점수_변형~건강만족도+가족의수입만족도+주거환경만족도+가족관계만족도+직업만족도+사회적친분관계만족도+여가생활만족도'
  test_df=model.pvalues.to_frame()
  if any(test_df[0]>0.05):
    if formula[formula.find(test_df.sort_values(by=0,ascending=False).index[0])-1]=="~":
      formula=formula.replace(test_df.sort_values(by=0,ascending=False).index[0],"")
    else:
      formula=formula.replace("+"+test_df.sort_values(by=0,ascending=False).index[0],"")
    return formula
  else:
    return False
