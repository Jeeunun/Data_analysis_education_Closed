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

# 스피어만 상관분석
from scipy.stats import spearmanr
def spearman_r(df):
    names = df.columns
    n = len(names)
    pv = 0.05

    data = []

    for i in range(0, n):
        # 기본적으로 i 다음 위치를 의미하지만 i가 마지막 인덱스일 경우 0으로 설정
        j = i + 1 if i < n - 1 else 0

        fields = names[i] + ' vs ' + names[j]
        s, p = spearmanr(df[names[i]], df[names[j]])
        result = p < pv

        data.append({'fields': fields, 'statistic': s, 'pvalue': p, 'result': result})

    rdf = DataFrame(data)
    rdf.set_index('fields', inplace=True)
    
    return rdf


# 회귀분석 결과보고 함수
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor

def ext_ols(data, y, x):
    """
    회귀분석을 수해한다.

    Parameters
    -------
    - data : 데이터 프레임
    - y: 종속변수 이름
    - x: 독립변수의 이름들(리스트)
    """

    # 독립변수의 이름이 리스트가 아니라면 리스트로 변환
    if type(x) != list:
        x = [x]

    # 종속변수~독립변수1+독립변수2+독립변수3+... 형태의 식을 생성
    expr = "%s~%s" % (y, "+".join(x))

    # 회귀모델 생성
    model = ols(expr, data=data)
    # 분석 수행
    fit = model.fit()

    # 파이썬 분석결과를 변수에 저장한다.
    summary = fit.summary()

    # 첫 번째, 세 번째 표의 내용을 딕셔너리로 분해
    my = {}

    for k in range(0, 3, 2):
        items = summary.tables[k].data
        # print(items)

        for item in items:
            # print(item)
            n = len(item)

            for i in range(0, n, 2):
                key = item[i].strip()[:-1]
                value = item[i+1].strip()

                if key and value:
                    my[key] = value

    # 두 번째 표의 내용을 딕셔너리로 분해하여 my에 추가
    my['variables'] = []
    name_list = list(data.columns)
    print(name_list)

    for i, v in enumerate(summary.tables[1].data):
        if i == 0:
            continue

        # 변수의 이름
        name = v[0].strip()
        
        vif = 0

        # 0번째인 Intercept는 제외
        if name in name_list:
            #변수의 이름 목록에서 현재 변수가 몇 번째 항목인지 찾기
            j = name_list.index(name)
            vif = variance_inflation_factor(data, j)

        my['variables'].append({
            "name": name,
            "coef": v[1].strip(),
            "std err": v[2].strip(),
            "t": v[3].strip(),
            "P-value": v[4].strip(),
            "Beta": 0,
            "VIF": vif,
        })

    # 결과표를 데이터프레임으로 구성
    mylist = []
    yname_list = []
    xname_list = []

    for i in my['variables']:
        if i['name'] == 'Intercept':
            continue

        yname_list.append(y)
        xname_list.append(i['name'])

        item = {
            "B": i['coef'],
            "표준오차": i['std err'],
            "β": i['Beta'],
            "t": "%s*" % i['t'],
            "유의확률": i['P-value'],
            "VIF": i["VIF"]
        }

        mylist.append(item)

    table = DataFrame(mylist,
                   index=MultiIndex.from_arrays([yname_list, xname_list], names=['종속변수', '독립변수']))
    
    # 분석결과
    result = "𝑅(%s), 𝑅^2(%s), 𝐹(%s), 유의확률(%s), Durbin-Watson(%s)" % (my['R-squared'], my['Adj. R-squared'], my['F-statistic'], my['Prob (F-statistic)'], my['Durbin-Watson'])

    # 모형 적합도 보고
    goodness = "%s에 대하여 %s로 예측하는 회귀분석을 실시한 결과, 이 회귀모형은 통계적으로 %s(F(%s,%s) = %s, p < 0.05)." % (y, ",".join(x), "유의하다" if float(my['Prob (F-statistic)']) < 0.05 else "유의하지 않다", my['Df Model'], my['Df Residuals'], my['F-statistic'])

    # 독립변수 보고
    varstr = []

    for i, v in enumerate(my['variables']):
        if i == 0:
            continue
        
        s = "%s의 회귀계수는 %s(p%s0.05)로, %s에 대하여 %s."
        k = s % (v['name'], v['coef'], "<" if float(v['P-value']) < 0.05 else '>', y, '유의미한 예측변인인 것으로 나타났다' if float(v['P-value']) < 0.05 else '유의하지 않은 예측변인인 것으로 나타났다')

        varstr.append(k)

    # 리턴
    return (model, fit, summary, table, result, goodness, varstr)