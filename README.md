# CheapChess - The Fastest Python Chess-AI
![license](https://img.shields.io/github/license/SiiiMiii/Chess-AI)
![activity](https://img.shields.io/github/commit-activity/m/SiiiMiii/Chess-AI)

> Combining Algorithmic Powers With The Beauty of Machine Learning
## Table of Contents
  - [Features](#features)
  - [How To Play](#how-to-play)
  - [Screenshots](#screenshots)
  - [Dependencies](#dependencies)
  - [Project Status](#project-status)
  - [Acknowledgements](#acknowledgements)
  - [Contact](#contact)

## Features
**Move Generation**
* precomputed data + procedual generation
* move- and attack-maps
* legal move generation considering pins and blocks
* handling (multiple) checks, pins... with 99%-100% accuracy
<br></br>

**State of the art search method**
* _DONE:_
  * minimax algorithm
  * alpha-beta pruning
  * move ordering
  * SHEF (Standard Heuristic Evaluation Function) - normal and piece-square-table based
  * Training data collection module for the SLEF model
* _IN PROGRESS:_
  * Object detection
  * Zobrist Hashing transposition handling
  * multiprocessing
* _TO-DO_
  * iterative deepening

**AlphaZero based approach**
* reinforcement learning by self-play
* Monte Carlo Tree Search (MCTS)
* Domain knowledge: game rules, position, legal moves → no domain-specific adaptations

## HOW TO PLAY
* clone this repo ```git clone https://github.com/Simuschlatz/CheapChess.git```
* run main file ```python3 main.py``` or ```python main.py```

    |Key|function|
    |---|--------|
    |space|unmake previous move|
    |a|watch ai play against itself|


## Screenshots
<img src="./assets/screenshots/15.11.jpeg" alt="screenshot" width="500"/>
<img src="./assets/screenshots/15.11(2).jpeg" alt="screenshot" width="500"/>

## Dependencies
**To run the current version of the app:**
* python 3
* numpy
* pygame

## Project-Status
Project is: _in progress_

## Acknowledgements
* Inspiration: [@SebLague](https://github.com/SebLague)
* Research done at [chessprogramming wiki](https://www.chessprogramming.org/)
