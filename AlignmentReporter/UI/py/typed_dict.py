from typing import TypedDict, List, Dict


class PlayerDict(TypedDict):
    """
    Player Data Dictionary template
    """
    Color: str
    Entries: List[str]
    Name: str


class DataDict(TypedDict):
    """
    Main Data Dictionary template
    """
    chb_image_title: bool
    cob_party_starting_alignment: str
    cob_players_select: int
    current_marker: int
    gb_add_auto_party: bool
    hs_current_scale: int
    hs_jpeg_qual: int
    hs_legend_h_offset: int
    hs_legend_stretch: int
    hs_legend_v_offset: int
    hs_line_quality: int
    hs_scale: int
    image_format: int
    le_current_custom: str
    le_image_title: str
    le_party_color: str
    le_party_name: str
    le_previous_custom: str
    legend_text_alignment: int
    out_path: str
    player: PlayerDict
    players: Dict[str, PlayerDict]
    previous_marker: int
    rb_average: bool
    sb_first_entry_weight: int
    sb_image_dpi: int
    sb_rolling_window_size: int
    title_alignment: int
