"""E5-small Adapter. 사용 전 SentenceTransformers·모델 가중치 준비 필요."""
from functools import lru_cache
import hashlib
from app.core.config import settings

@lru_cache(maxsize=1)
def get_model():
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(1)
    return SentenceTransformer(settings.embedding_model,device='cpu')


def encode(texts:list[str],kind:str='passage')->list[list[float]]:
    """TODO B-10 · encode() — mentor와 동일한 함수 계약을 완성하세요."""
    if kind not in ('query','passage'):raise ValueError('kind는 query 또는 passage여야 합니다.')
    if not texts:return []
    prefixed=[f'{kind}: {s}' for s in texts]
    model=get_model()
    tokenizer=getattr(model,'tokenizer',None)
    max_length=getattr(model,'max_seq_length',None)
    if tokenizer is not None and isinstance(max_length,int) and max_length>0:
        input_ids=tokenizer(prefixed,add_special_tokens=True,truncation=False)['input_ids']
        if any(len(ids)>max_length for ids in input_ids):
            raise ValueError(f'E5 토큰 길이가 모델 한도 {max_length}을 초과합니다.')
    vectors=model.encode(prefixed,normalize_embeddings=True,batch_size=16,
                         show_progress_bar=False)
    rows=[v.tolist() for v in vectors]
    if any(len(v)!=384 for v in rows):raise RuntimeError('Embedding 차원이 384가 아닙니다.')
    return rows
    # TODO B-10: E5 query/passage Prefix, normalize_embeddings=True, max_seq_length
    # TODO B-10: 검증, 384차원 벡터를 반환하세요. 실제 모델 호출만 성공으로 인정합니다.
    # 입력·반환형과 예외·상태코드는 요구사항 명세서/API 계약을 참조합니다.

def overview_hash(s:str)->str:
    # 해시 기준: 저장된 Overview의 UTF-8 원문. Prefix는 저장해시에서 제외합니다.
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
