# iTrash: Incentivized Token Rewards for Automated Sorting and Handling

The **Incentivized Token Rewards for Automated Sorting and Handling** (iTrash) aims to create an intelligent trashcan that incentivizes people to recycle by giving rewards using blockchain technology. 


## Context
The project was developed by Pablo Ortega under the supervision of Eduardo Castello Ferrer. 


## Abstract
As robotic systems (RS) become more autonomous, they are becoming increasingly used in small spaces and offices to automate tasks such as cleaning, infrastructure maintenance, or resource management. In this paper, we propose iTrash, an intelligent trashcan that aims to improve recycling rates in small office spaces. For that, we ran a 5 day experiment and found that iTrash can produce an efficiency increase of more than 30% compared to traditional trashcans. The findings derived from this work, point to the fact that using iTrash not only increase recyclying rates, but also provides valuable data such as users behaviour or bin usage patterns, which cannot be taken from a normal trashcan. This information can be used to predict and optimize some tasks in these spaces. Finally, we explored the potential of using blockchain technology to create economic incentives for recycling, following a Save-as-you-Throw (SAYT) model. 


## Components

| Component | Description | Code |
| --- | --- | --- |
| System | System pipeline with the different components | [System](system) |
| QR Code App | App to scan QRs for the rewards  | [QR Code App](qr_app) |
| Labelling app | App to label manually the different images | [Labelling app](post-experiments/app-labelling) |
| Analysis Pipeline | Pipeline where we extract features from the experiments | [Analysis Pipeline](post-experiments/data_analysis) |



## Other Resources
[Youtube](https://www.youtube.com/watch?v=sdrd5JMhjsk)     

[Paper](https://arxiv.org/abs/2502.18161)







