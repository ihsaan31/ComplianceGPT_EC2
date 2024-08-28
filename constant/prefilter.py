import pickle

with open('constant/peraturan_dicabut.pkl', 'rb') as f:
        peraturan_dicabut = pickle.load(f)

FILTER_BI = [
        {
            "bool": {
                "must_not": {
                    "terms": {
                        "metadata.regulation_number.keyword": peraturan_dicabut
                    }
                },
                "must": [
                    {
                        "term": {
                            "metadata.sector.keyword": "Perbankan"
                        }
                    }
                ]
            }
        }
    ]

FILTER_OJK = [
        {
            "bool": {
                "must_not": {
                    "terms": {
                        "metadata.regulation_number.keyword": peraturan_dicabut
                    }
                },
                "must": [
                    {
                        "term": {
                            "metadata.subsector.keyword": "Bank Umum"
                        }
                    }
                ]
            }
        }
    ]

FILTER_SIKEPO = [
    {
        "bool": {
            "must_not": {
                "terms": {
                    "metadata.Nomor Ketentuan.keyword": peraturan_dicabut
                }
            },
            "must": [
                {
                    "term": {
                        "metadata.Kodifikasi Ketentuan.keyword": "Bank Umum Konvensional"
                    }
                }
            ]
        }
    }
]

# filter_dict = [{"bool": {"must_not": {"terms": {"metadata.regulation_number.keyword": peraturan_dicabut}}}}]
