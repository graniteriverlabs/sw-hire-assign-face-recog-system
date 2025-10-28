# Architecture Diagram

This document provides architecture diagram for the gesture recognition system.


```mermaid
graph TB
    CONFIG[config.json<br/>Single Source of Truth]
  
    subgraph "Mode Selection"
        MODE_STATIC[mode: 'static']
        MODE_DYNAMIC[mode: 'dynamic']
    end
  
    subgraph "Approach Selection"
        APP_MP[approach: 'mediapipe']
        APP_SMOL[approach: 'smolvlm']
    end
  
    subgraph "Dynamic Settings"
        DYN_ENABLED[dynamic.enabled: true]
        DYN_THRESH[dynamic.performance_thresholds]
        DYN_WINDOW[dynamic.evaluation_window: 5]
        DYN_COOLDOWN[dynamic.switch_cooldown_seconds: 10]
    end
  
    CONFIG --> MODE_STATIC
    CONFIG --> MODE_DYNAMIC
  
    CONFIG --> APP_MP
    CONFIG --> APP_SMOL
  
    CONFIG --> DYN_ENABLED
    CONFIG --> DYN_THRESH
    CONFIG --> DYN_WINDOW
    CONFIG --> DYN_COOLDOWN
  
    MODE_STATIC --> EXEC_STATIC[Execute Static Mode]
    MODE_DYNAMIC --> EXEC_DYNAMIC[Execute Dynamic Mode]
  
    APP_MP --> LOAD_MP[Load MediaPipe Module]
    APP_SMOL --> LOAD_SMOL[Load SmolVLM Module]
  
    EXEC_STATIC --> LOAD_MP
    EXEC_STATIC --> LOAD_SMOL
  
    EXEC_DYNAMIC --> DYN_ENABLED
    DYN_ENABLED --> MONITOR[Start Monitoring]
    DYN_THRESH --> MONITOR
    DYN_WINDOW --> MONITOR
    DYN_COOLDOWN --> MONITOR
  
    MONITOR --> LOAD_MP
    MONITOR --> LOAD_SMOL
```

<style>#mermaid-1761630699871{font-family:sans-serif;font-size:16px;fill:#333;}#mermaid-1761630699871 .error-icon{fill:#552222;}#mermaid-1761630699871 .error-text{fill:#552222;stroke:#552222;}#mermaid-1761630699871 .edge-thickness-normal{stroke-width:2px;}#mermaid-1761630699871 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-1761630699871 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-1761630699871 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-1761630699871 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-1761630699871 .marker{fill:#333333;}#mermaid-1761630699871 .marker.cross{stroke:#333333;}#mermaid-1761630699871 svg{font-family:sans-serif;font-size:16px;}#mermaid-1761630699871 .label{font-family:sans-serif;color:#333;}#mermaid-1761630699871 .label text{fill:#333;}#mermaid-1761630699871 .node rect,#mermaid-1761630699871 .node circle,#mermaid-1761630699871 .node ellipse,#mermaid-1761630699871 .node polygon,#mermaid-1761630699871 .node path{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaid-1761630699871 .node .label{text-align:center;}#mermaid-1761630699871 .node.clickable{cursor:pointer;}#mermaid-1761630699871 .arrowheadPath{fill:#333333;}#mermaid-1761630699871 .edgePath .path{stroke:#333333;stroke-width:1.5px;}#mermaid-1761630699871 .flowchart-link{stroke:#333333;fill:none;}#mermaid-1761630699871 .edgeLabel{background-color:#e8e8e8;text-align:center;}#mermaid-1761630699871 .edgeLabel rect{opacity:0.5;background-color:#e8e8e8;fill:#e8e8e8;}#mermaid-1761630699871 .cluster rect{fill:#ffffde;stroke:#aaaa33;stroke-width:1px;}#mermaid-1761630699871 .cluster text{fill:#333;}#mermaid-1761630699871 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:sans-serif;font-size:12px;background:hsl(80,100%,96.2745098039%);border:1px solid #aaaa33;border-radius:2px;pointer-events:none;z-index:100;}#mermaid-1761630699871:root{--mermaid-font-family:sans-serif;}#mermaid-1761630699871:root{--mermaid-alt-font-family:sans-serif;}#mermaid-1761630699871 flowchart{fill:apa;}</style>

<style>#mermaid-1761630699974{font-family:sans-serif;font-size:16px;fill:#333;}#mermaid-1761630699974 .error-icon{fill:#552222;}#mermaid-1761630699974 .error-text{fill:#552222;stroke:#552222;}#mermaid-1761630699974 .edge-thickness-normal{stroke-width:2px;}#mermaid-1761630699974 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-1761630699974 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-1761630699974 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-1761630699974 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-1761630699974 .marker{fill:#333333;}#mermaid-1761630699974 .marker.cross{stroke:#333333;}#mermaid-1761630699974 svg{font-family:sans-serif;font-size:16px;}#mermaid-1761630699974 .label{font-family:sans-serif;color:#333;}#mermaid-1761630699974 .label text{fill:#333;}#mermaid-1761630699974 .node rect,#mermaid-1761630699974 .node circle,#mermaid-1761630699974 .node ellipse,#mermaid-1761630699974 .node polygon,#mermaid-1761630699974 .node path{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaid-1761630699974 .node .label{text-align:center;}#mermaid-1761630699974 .node.clickable{cursor:pointer;}#mermaid-1761630699974 .arrowheadPath{fill:#333333;}#mermaid-1761630699974 .edgePath .path{stroke:#333333;stroke-width:1.5px;}#mermaid-1761630699974 .flowchart-link{stroke:#333333;fill:none;}#mermaid-1761630699974 .edgeLabel{background-color:#e8e8e8;text-align:center;}#mermaid-1761630699974 .edgeLabel rect{opacity:0.5;background-color:#e8e8e8;fill:#e8e8e8;}#mermaid-1761630699974 .cluster rect{fill:#ffffde;stroke:#aaaa33;stroke-width:1px;}#mermaid-1761630699974 .cluster text{fill:#333;}#mermaid-1761630699974 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:sans-serif;font-size:12px;background:hsl(80,100%,96.2745098039%);border:1px solid #aaaa33;border-radius:2px;pointer-events:none;z-index:100;}#mermaid-1761630699974:root{--mermaid-font-family:sans-serif;}#mermaid-1761630699974:root{--mermaid-alt-font-family:sans-serif;}#mermaid-1761630699974 flowchart{fill:apa;}</style>
