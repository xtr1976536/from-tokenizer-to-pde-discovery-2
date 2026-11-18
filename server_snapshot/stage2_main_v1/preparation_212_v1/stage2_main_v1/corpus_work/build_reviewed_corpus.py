from curation import save
from review_batch_a import build as build_a
from review_batch_b import build as build_b
from review_batch_c import build as build_c
from review_batch_d import build as build_d
from review_batch_e import build as build_e
from review_batch_f import build as build_f
from review_batch_g import build as build_g
from review_batch_h import build as build_h
from review_batch_i import build as build_i
from review_batch_j import build as build_j
from review_batch_k import build as build_k
from review_batch_l import build as build_l
from review_batch_m import build as build_m
from review_batch_n import build as build_n
from review_batch_o import build as build_o
from review_batch_p import build as build_p
from legacy_pdf_reuse import build as build_legacy_pdf
from review_batch_q import build as build_q
from review_batch_r import build as build_r
from review_batch_s import build as build_s
from review_batch_t import build as build_t
from review_batch_u import build as build_u
from review_batch_v import build as build_v


if __name__ == '__main__':
    save(build_a() + build_b() + build_c() + build_d() + build_e() + build_f() + build_g() + build_h() + build_i() + build_j() + build_k() + build_l() + build_m() + build_n() + build_o() + build_p() + build_legacy_pdf() + build_q() + build_r() + build_s() + build_t() + build_u() + build_v())
