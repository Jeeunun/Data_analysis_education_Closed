import numpy as np
from pandas import DataFrame
from sklearn.impute import SimpleImputer

# 결측치경계 구하기 함수
def getIq(field):
    q1 = field.quantile(q=0.25)
    q3 = field.quantile(q=0.75)
    iqr = q3 - q1
    하한 = q1 - 1.5 * iqr
    상한 = q3 + 1.5 * iqr
    결측치경계 = [하한, 상한]
    return 결측치경계

# 이상치를 결측치로 변경 함수
def replaceOutlier(df, fieldName):
    cdf = df.copy()

    # fieldName이 List가 아니면 List로 변환
    if not isinstance(fieldName, list):
        fieldName = [fieldName]

    for f in fieldName:
        결측치경계 = getIq(cdf[f])
        cdf.loc[cdf[f] < 결측치경계[0], f] = np.nan
        cdf.loc[cdf[f] > 결측치경계[1], f] = np.nan

    return cdf

# 결측치에 대한 처리 함수
def replaceMissingValue(df):
    imr = SimpleImputer(missing_values=np.nan, strategy='mean')
    df_imr = imr.fit_transform(df.values)
    re_df = DataFrame(df_imr, index=df.index, columns=df.columns)
    return re_df


# stopwords 지우는 함수 [워드클라우드]
def clearStopwords(nouns, stopwords_file_path="wordcloud/stopwords-ko.txt"):
    with open(stopwords_file_path, 'r', encoding='utf-8') as f:
        stopwords = f.readlines()

        # stopwords에서 공백 지우고 리스트로
        for i,v in enumerate(stopwords):
            stopwords[i] = v.strip()

        data_set = []

        for v in nouns:
            if v not in stopwords:
                data_set.append(v)

        return data_set
    


# 신뢰구간 함수
def get_confidence_interval(data, clevel=0.95):
    n = len(data)                                                       #샘플사이즈
    dof = n-1                                                           #자유도
    sample_mean = data.mean()                                           #표본평균
    sample_std = data.std(ddof=1)                                       #표본표준편차
    sample_std_error = sample_std / sqrt(n)                             #표본표준오차
    #신뢰구간
    cmin, cmax = t.interval(clevel, dof, sample_mean, sample_std_error )
    return(cmin, cmax)

# <일원분산분석> 정규성 검증 함수
from pandas import DataFrame, MultiIndex
from scipy.stats import shapiro, normaltest, ks_2samp

def normality_test(*any):
    names = []

    result = {
        'statistic' : [],
        'p-value' : [],
        'result' : []
    }

    for i in any:
        s, p = shapiro(i)
        result['statistic'].append(s)
        result['p-value'].append(p)
        result['result'].append(p > 0.05)
        names.append(('정규성', 'shapiro', i.name))

    for i in any:
        s, p = normaltest(i)
        result['statistic'].append(s)
        result['p-value'].append(p)
        result['result'].append(p > 0.05)
        names.append(('정규성', 'normaltest', i.name))  

    n = len(any)

    for i in range(0,n):
        j = i + 1 if i < n-1 else 0

        s, p = ks_2samp(any[i], any[j])
        result['statistic'].append(s)
        result['p-value'].append(p)
        result['result'].append(p > 0.05)
        names.append(('정규성', 'ks_2samp', f'{any[i].name} vs {any[j].name}'))

    return DataFrame(result, index=MultiIndex.from_tuples(names, name = ['condition','test','field']))     


# <일원분산분석> 등분산성 검증 함수
from scipy.stats import bartlett, fligner, levene

def equal_variance_test(*any):
    s1, p1 = bartlett(*any)
    s2, p2 = fligner(*any)
    s3, p3 = levene(*any)

    names = []

    for i in any:
        names.append(i.name)

    fix = " vs "
    name = fix.join(names)
    index = [['등분산성', 'Bartlett', name], ['등분산성', 'Fligner', name], ['등분산성', 'Levene', name]]
    
    df = DataFrame({
        'statistic': [s1, s2, s3],
        'p-value': [p1, p2, p3],
        'equal-var': [p1 > 0.05, p2 > 0.05, p3 > 0.05]
    }, index=MultiIndex.from_tuples(index, names=['condition', 'test','field']))

    return df

# <일원분산분석> 독립성 검증 함수
from pandas import DataFrame
from scipy.stats import chi2_contingency

def independence_test(*any):
    df = DataFrame(any).T
    result = chi2_contingency(df) #result = 객체
    
    names = []
    for i in any:
        names.append(i.name)

    fix = " vs "
    name = fix.join(names)

    index = [['독립성','chi2', name]]

    df = DataFrame({
        'statistic' : [result.statistic],
        'p-value' : [result.pvalue],
        'result' : [result.pvalue > 0.05]
    }, index = MultiIndex.from_tuples(index, names=['condition','test','field']))
    
    return df

# <일원분산분석> 모든 조건성 검사 함수
from pandas import concat

def all_test(*any):
    return concat([normality_test(*any), equal_variance_test(*any), independence_test(*any)])


# 여러변수의 상관분석 = 상관도행렬 반복문 함수
from scipy.stats import t, pearsonr


def pearson_r(df):
    names = df.columns
    n=len(names)
    pv=0.05

    data = []

    for i in range(0,n):
        j = i+1 if i<n-1 else 0

        fields = names[i] + 'vs' + names[j]
        s, p = pearsonr(df[names[i]], df[names[j]])
        result = p < pv

        data.append({'fields': fields, 'statistic': s, 'pvalue': p, 'result': result})

    rdf = DataFrame(data)
    rdf.set_index('fields', inplace=True)

    return rdf