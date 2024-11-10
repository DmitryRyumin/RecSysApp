"""
File: html_components.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: HTML components.
License: MIT License
"""

ADD_RANGE = """\
<div class="range range-usefulness">
    <label for="usefulness-current">{}</label>
    <div class="slider-container" id="usefulness-current">
    </div>
</div>
<div class="range range-demand">
    <label for="demand-future">{}</label>
    <div class="slider-container" id="demand-future">
    </div>
</div>
<div class="range range-interface">
    <label for="interface-current">{}</label>
    <div class="slider-container" id="interface-current">
    </div>
</div>
"""
