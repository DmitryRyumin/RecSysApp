"""
File: html_components.py
Author: Dmitry Ryumin
Description: HTML components.
License: MIT License
"""

ADD_RANGE = """\
<div class="range range-usefulness">
    <label for="usefulness-current">Насколько полезно данное приложение в его нынешнем виде?</label>
    <div class="slider-container" id="usefulness-current">
    </div>
</div>
<div class="range range-demand">
    <label for="demand-future">Насколько было бы востребовано данное приложение в доработанном виде?</label>
    <div class="slider-container" id="demand-future">
    </div>
</div>
<div class="range range-interface">
    <label for="interface-current">Насколько удобен интерфейс в его нынешнем виде?</label>
    <div class="slider-container" id="interface-current">
    </div>
</div>
"""
