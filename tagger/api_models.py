# api_models.py — Forge 互換パッチ v2
# -------------------------------------------------------------
# 2025‑05‑17 kitamo patch (v2)
# - Forge の API 名変更や import パスの差異ですべて動くように
#   * InterrogateRequest/Response が存在しなければ自動 alias
#   * それでも見つからなければダミー BaseModel を作成
# -------------------------------------------------------------

from __future__ import annotations
from typing import Dict, List, Optional, Any
import importlib
import types

from pydantic import BaseModel, Field

# -------------------------------------------------------------
# 1) modules.api.models を安全に import
# -------------------------------------------------------------
try:
    _api_models = importlib.import_module("modules.api.models")
except Exception:
    # Forge の構成がさらに変わっている場合は空モジュールを作る
    _api_models = types.ModuleType("modules.api.models")  # type: ignore

# -------------------------------------------------------------
# 2) Forge で改名されたクラスを旧名にマップ
# -------------------------------------------------------------
if not hasattr(_api_models, "InterrogateRequest"):
    # ReqInterrogate → InterrogateRequest
    if hasattr(_api_models, "ReqInterrogate"):
        _api_models.InterrogateRequest = _api_models.ReqInterrogate  # type: ignore
if not hasattr(_api_models, "InterrogateResponse"):
    # ResInterrogate → InterrogateResponse
    if hasattr(_api_models, "ResInterrogate"):
        _api_models.InterrogateResponse = _api_models.ResInterrogate  # type: ignore

# -------------------------------------------------------------
# 3) InterrogateRequest / Response がまだ無ければダミー定義
#    （必要最低限のフィールドだけ）
# -------------------------------------------------------------
if not hasattr(_api_models, "InterrogateRequest"):
    class _DummyInterrogateRequest(BaseModel):  # type: ignore
        image: str = Field(..., description="Base64 encoded image")
        model: Optional[str] = None
        prompt: Optional[str] = None
        # 他フィールドは Tagger では使わないので省略
    _api_models.InterrogateRequest = _DummyInterrogateRequest  # type: ignore

if not hasattr(_api_models, "InterrogateResponse"):
    class _DummyInterrogateResponse(BaseModel):  # type: ignore
        caption: Dict[str, float]
    _api_models.InterrogateResponse = _DummyInterrogateResponse  # type: ignore

# -------------------------------------------------------------
# 4) 以降は Tagger 独自モデル
# -------------------------------------------------------------
sd_models = _api_models  # 互換のため元変数名に合わせる


class TaggerInterrogateRequest(sd_models.InterrogateRequest):  # type: ignore
    """
    Tagger 用 interrogate リクエストモデル
    """

    model: str = Field(
        title="Model",
        description="使用するタグガーモデル名（例: wd14-vit.v3）",
    )
    threshold: float = Field(
        default=0.35,
        ge=0,
        le=1,
        title="Threshold",
        description="この確率未満のタグを除外するしきい値",
    )


class TaggerInterrogateResponse(BaseModel):
    """
    Tagger interrogate レスポンス
    """

    caption: Dict[str, float] = Field(
        title="Caption",
        description="tag → 確率 の辞書",
    )


class InterrogatorsResponse(BaseModel):
    """
    利用可能な interrogator モデル一覧
    """

    models: List[str] = Field(
        title="Models",
        description="使用可能な interrogator の識別子リスト",
    )
