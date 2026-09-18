# Lab 08 - Tesla P/E Comparable-Company Triangulation
Target: Tesla, Inc. (TSLA)
Comparison date: September 17, 2026
Question: What would one Tesla share be worth at defensible peer P/E multiples, and how does that compare with my Week 3 DCF?
## Peer Policy
- I will be investigating publicly traded companies that manufacture and sell vehicles (especially EVs) at scale. I will take into consideration where the majority of their earnings originate from (tech, auto, service, etc.) in comparison to Tesla's. Annual GAAP diluted EPS will only be used if it is public by today's comparison date. A company will be excluded from positive P/E calculation if annual GAAP diluted EPS is zero or negative.  
AI-suggestion addition: This P/E comparison is a narrow test of Tesla’s vehicle-manufacturing earnings rather than a complete valuation of Tesla’s energy, software, autonomy, or Robotaxi opportunities.
## Candidate research and decisions
SOURCES:
TSLA sources: tsla-20251231 annual 10-K report
GM : gm-20251231 annual 10k report     https:investor.gm.com/static-files/36170429-ef23-4ad5-97dd-6a523c3f8deb
https://finance.yahoo.com/quoteGM/
Rivian (RIVN): rivn-20251231 annual 10k report
https://finance.yahoo.com/quote/RIVN/

DECISIONS:
TSLA: 
    close price = 366.20, FY2025 GAAP diluted EPS = 1.08
GM: 
    close price = 86.59, FY2025 GAAP diluted EPS = 3.27
    Decision: Use as peer. GM is another large vehicle manufacturer but has many differences from TSLA.
RIVN: 
    close price = 15.40, FY2025 GAAP diluted EPS = -3.07, 
    Decision: exclude p/e (normal positive p/e not useful due to diluted loss per share)
## Calculator output
/E Comparable-Company Calculator
Target: TSLA
Excluded RIVN: nonpositive or missing price/EPS

PEER MULTIPLES
GM P/E: 26.480122x
Full-peer estimate: one-peer reference estimate = $28.60

LEAVE-ONE-OUT CHECK
Remove GM: no usable peers; no estimate.
## Validation
GM P/E by hand: 26.480122
One-peer reference estimate (using GM P/E): 28.60 per TSLA share 
- calculator reports no estimate, which is correct
## DCF comparison
Method        Result and date       Main assumption or limitation
 ━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━
   Week 3 DCF    $43.93 per share,     Depends on my FCFF    growth path, WACC, terminal-growth rate, and          enterprise-to-  equity bridge.
  ────────────  ────────────────────  ─────────────────────
   Peer P/E      $28.60 one-peer       Depends on GM as a peer, as Rivian’s negative GAAP EPS prevents a two-peer P/E range.

## Skeptical-AI review
Output Question: If your stated policy requires matching where the majority of earnings originate, why anchor Tesla's multiple to a legacy ICE truck/SUV manufacturer instead of constructing a multi-variable peer set that weights scaled auto operations against high-margin energy and software businesses?
ACCEPT JUDGEMENT: According to the FY2025 revenue report, automotive sales were still a majority of the annual revenue, which is why I saw GM as a relevant peer referene. However, the AI judgement is correct in that GM is not an accurate or complete representation of Tesla due to the difference of ICE and Tesla software and Robotaxi expectations in the future. GM does not capture all of Tesla's maine revenue drivers but serves as a solid comparison. 
## Reflection
My Tesla DCF and the GM P/E are both far below today's market price, but I believe the comparison has the large handicap/limitation of differences in business models and growth between the two. For that reason, I will watch-defer. I would reconsider if Tesla were to report higher automobile , Robotaxi, and AI developments are producing a CF above what I currently have in my assumptions. For now, I will monitor FCF and progress towards energy storage and Robotaxi economics for TSLA to see how they may change my base assumptions.