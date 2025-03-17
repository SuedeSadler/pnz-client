from jwcrypto import jwt, jwk

key =  {
            "alg": "PS256",
            "e": "AQAB",
            "kid": "MWNZ-KeyId-1",
            "kty": "RSA",
            "n": "pmtRHdvlPSZrXp430IrTeA1bApXvObK2LPEsm_sA54TIJM5kDfotiCmj3O5ylEEJnkzuK8AcyCeZcEd8oyPVorbyBq_pnMYMKjxXkQ2sofaxED5V_m3cYbp2UVcnjCJycteb3958lk3GZ99cZjXBvewyNuTqRLltqPZFIkKSfKRU62jSQOo3nrGSAe129PMBHUq0Wymm1t-ztOXFe0G85cWPoMk7xqtYhhrdJcnXlatEGP8Ro5K2bAkzVslgGSgg9aXMrLcwdkbY7G1FUnosJNdAXwk7lLs1msfZTVMCcLNng67z7RzLA4ghSxc1LwOjc2_2Figsiy15src1t8uQqWxgrjccroxgZnUY_PkF5LeAIIf26ssWR1d59Zq90LuCk4m7RhADIYdDGfxg6_tFaTblWG9xWEzDrzTJ4d20DX_t6fY3ZbVpjjU-ehOePwr7LlR8R7GRQx74DZpVW2iQIan3YemHF25gmrqQMpzUPFb-VxcY2IfNtehi1w9e99CzmlQDFvAhWyegLwKFOYJdtKECw9c3ZPB8WFIbqul6NBpLOoEXxI_ERCsXbI8T3i7KlsapxEahkJoLzNFLBP0SczNhZVIpC6Jh0frdp6MRVM7RjtW1wrTgIH7GPYL_8AdL5zZbk_QcBLQGGJL-eXd6OWd5aov2pGsJsEt3K1PWBIs",
            "use": "sig"
        }
jsonKey = jwk.JWK(**key)

print(jsonKey.export_to_pem().decode('utf-8'))
