window.HIDDEN_LAYER_PRIMER = {
  title: "Treasury Hidden Market Layer Primer",
  introduction:
    "The visible yield curve is the market's macro surface. The hidden layer is where Treasury pricing is bent by financing, delivery, inventory, liquidity, and crowding. This handbook is meant to be reread. Each section follows the same order: what the concept means, why desks care, the exact desk vocabulary, the variables professionals monitor, the public proxies you can actually collect, and the gap between public ex-post evidence and real desk-time visibility.",
  studyFramework: [
    "Start with the visible move in the curve, breakevens, and real yields.",
    "Ask whether macro alone explains the move or whether market structure likely bent it.",
    "Use desk terminology carefully: cheapening, richness, tail, specialness, squeeze, concession, and digestion all mean different things.",
    "Treat public data as delayed instrumentation. It is good for disciplined review, not perfect live flow reconstruction.",
    "End each section with the same question: how should this change my regime interpretation?"
  ],
  layers: [
    {
      id: "balance-sheet-pressure",
      number: "1",
      title: "Balance-sheet pressure",
      strapline: "When dealer intermediation capacity becomes scarce or expensive.",
      deskSpeed: "Intraday to weekly",
      publicRhythm: "Daily funding proxies, weekly dealer confirmation",
      definition:
        "Balance-sheet pressure means the main intermediaries of the Treasury market, especially primary dealers and financing desks, become less willing or less able to absorb additional Treasury risk. The market still clears, but it clears at a cheaper price or higher yield because warehousing inventory has become expensive.",
      whyDeskCares:
        "A macro move can be real and still be amplified by balance-sheet strain. If you mistake dealer-capacity stress for a pure regime repricing, you can overread the macro message and underread the plumbing.",
      implications: [
        "Cash Treasuries may cheapen faster than a clean macro model would suggest.",
        "Auctions often need more concession before they clear smoothly.",
        "Swap spreads can move in unusual ways because Treasury cash and derivative markets are being intermediated under different constraints.",
        "Liquidity can look acceptable in headlines but still feel expensive in actual inventory transfer."
      ],
      terminology: [
        {
          term: "Cash bonds cheapening",
          meaning:
            "The actual Treasury security falls in price or rises in yield relative to nearby instruments, curve neighbors, or a fair-value estimate.",
          deskRead:
            "The market is asking for a better entry yield before it will hold the bond."
        },
        {
          term: "Swap spreads moving oddly",
          meaning:
            "The gap between swap rates and Treasury yields changes in a way that looks inconsistent with a simple macro story.",
          deskRead:
            "Balance-sheet cost, collateral pressure, or supply friction may be distorting cash Treasuries."
        },
        {
          term: "Auction indigestion",
          meaning:
            "New Treasury supply is not being absorbed cleanly after an auction, so the issue stays weak and dealers remain stuck with more risk.",
          deskRead:
            "The street took down the bonds, but the real money handoff was not smooth."
        },
        {
          term: "Street is full",
          meaning:
            "Dealers and leveraged intermediaries already carry enough of the relevant sector, so marginal capacity is thin.",
          deskRead:
            "The next seller needs to offer better yield, because balance-sheet inventory is already crowded."
        }
      ],
      deskVariables: [
        {
          name: "Primary dealer net positions",
          description:
            "Weekly or internal inventory measures showing how much Treasury risk dealers are already carrying.",
          whyItMatters:
            "Large positions mean the street has less spare capacity to warehouse new paper."
        },
        {
          name: "Dealer financing usage",
          description:
            "How much dealers are borrowing or lending against securities in repo or related funding channels.",
          whyItMatters:
            "Rising financing usage can signal balance-sheet intensity even before outright stress shows up."
        },
        {
          name: "Swap spreads",
          description:
            "The gap between swap rates and Treasury yields at the same maturity.",
          whyItMatters:
            "This often captures whether Treasury cash is under pressure relative to derivatives."
        },
        {
          name: "When-issued concession and auction tail",
          description:
            "The yield concession before an auction and the gap between the auction stop-out and the when-issued level.",
          whyItMatters:
            "More concession and larger tails are classic signs that supply needs balance-sheet compensation."
        }
      ],
      publicInstruments: [
        {
          source: "New York Fed Primary Dealer Statistics",
          description:
            "Official weekly inventory, financing, and transaction statistics for primary dealers.",
          frequency: "Weekly",
          publishTiming: "Thursdays around 4:15 p.m. ET for the previous week",
          use: "Confirms whether dealer positions and financing load are building.",
          gap: "Useful but slow and aggregated. A live desk sees the pressure intraday and by sector before the weekly official print.",
          link: "https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics"
        },
        {
          source: "New York Fed SOFR, TGCR, BGCR, OBFR",
          description:
            "Official overnight funding benchmarks for secured and unsecured money markets.",
          frequency: "Daily business days",
          publishTiming: "Morning publication with possible same-day revisions",
          use: "Shows whether broad Treasury financing conditions are tightening or diverging.",
          gap: "Strong as a public funding gauge, but it does not show the live sector-by-sector inventory stress a desk sees.",
          link: "https://www.newyorkfed.org/markets/reference-rates"
        },
        {
          source: "OFR Short-Term Funding Monitor",
          description:
            "Public monitor for repo and related short-term funding conditions.",
          frequency: "Daily refresh for many series",
          publishTiming: "Typically refreshed on weekdays",
          use: "Adds breadth to the funding picture and helps identify collateralized funding strain.",
          gap: "Still ex-post and aggregated rather than a live dealer financing screen.",
          link: "https://www.financialresearch.gov/short-term-funding-monitor/api/"
        },
        {
          source: "FINRA Treasury trade transparency",
          description:
            "Next-day Treasury transaction transparency and aggregate volume files for public users.",
          frequency: "Daily",
          publishTiming: "Following morning for transaction data; evening files for aggregates",
          use: "Shows whether stress days also had unusually heavy on-the-run trading and turnover.",
          gap: "Helpful for review, but not a real-time view of dealer books or client inquiry.",
          link: "https://www.finra.org/finra-data/fixed-income/about-treasuries"
        }
      ],
      researchUse:
        "Use balance-sheet pressure as a hidden-layer inference. Let daily funding and curve behavior suggest it, then use weekly dealer statistics as the confirming evidence rather than the first signal."
    },
    {
      id: "futures-basis-dislocations",
      number: "2",
      title: "Futures-basis dislocations",
      strapline: "When Treasury futures and cash bonds stop lining up cleanly.",
      deskSpeed: "Intraday to daily",
      publicRhythm: "Daily to weekly; real-time view is limited",
      definition:
        "A futures-basis dislocation appears when the Treasury futures contract and the underlying deliverable cash bond imply inconsistent pricing after adjusting for conversion factors, carry, and financing. It is not just a pricing oddity; it is often a funding and leverage story.",
      whyDeskCares:
        "Many relative-value funds and macro desks express Treasury views through futures against cash. When the basis stretches too far, it can become a signal of financing stress, crowded leverage, delivery pressure, or an opportunity if the gap later closes.",
      implications: [
        "The apparent yield-curve move may partly reflect futures-cash plumbing rather than pure macro repricing.",
        "CTD dynamics can push one maturity sector around even if the macro news is broad-based.",
        "Levered basis trades can behave like hidden volatility sellers until financing or delivery conditions break."
      ],
      terminology: [
        {
          term: "Gross basis",
          meaning:
            "The simple price gap between the futures contract and the underlying cash bond after conversion adjustment.",
          deskRead:
            "It shows the headline dislocation before financing is fully taken into account."
        },
        {
          term: "Net basis",
          meaning:
            "The basis after adjusting for repo financing, carry, and delivery economics.",
          deskRead:
            "This is closer to the actual economic trade a basis desk evaluates."
        },
        {
          term: "CTD",
          meaning:
            "The cheapest-to-deliver bond into the futures contract.",
          deskRead:
            "The futures contract is really trading a delivery option around this bond, not a generic maturity point."
        },
        {
          term: "Implied repo",
          meaning:
            "The financing rate implied by the futures-cash relationship.",
          deskRead:
            "If implied repo diverges from actual funding, the basis can signal a trade or a stress point."
        }
      ],
      deskVariables: [
        {
          name: "Futures price and conversion factor",
          description:
            "The contract price plus the standardized conversion applied to eligible deliverables.",
          whyItMatters:
            "You need both to identify whether futures are rich or cheap to the cash market."
        },
        {
          name: "CTD yield and cash price",
          description:
            "The live pricing of the bond most likely to be delivered into the contract.",
          whyItMatters:
            "The CTD is the bond that carries most of the delivery economics."
        },
        {
          name: "Implied repo versus actual repo",
          description:
            "The financing rate inferred from the futures-cash relationship compared with what the desk can actually borrow at.",
          whyItMatters:
            "A large wedge is where the economic basis trade either becomes attractive or unstable."
        },
        {
          name: "Futures open interest and roll behavior",
          description:
            "Open contracts and the richness or cheapness of the roll into the next contract month.",
          whyItMatters:
            "Crowded positioning and stressed rolls often turn a quiet basis trade into a violent unwind."
        }
      ],
      publicInstruments: [
        {
          source: "CME Treasury futures market pages",
          description:
            "Public contract specifications, delayed quotes, and educational material around Treasury futures.",
          frequency: "Real-time with license; delayed/public views otherwise",
          publishTiming: "Exchange-time updates",
          use: "Anchor futures pricing, contract design, and delivery context.",
          gap: "A real desk has full order-book, CTD, and basis analytics; public users mostly see delayed or simplified views.",
          link: "https://www.cmegroup.com/markets/interest-rates/us-treasury.html"
        },
        {
          source: "CFTC Commitments of Traders",
          description:
            "Weekly positioning data for leveraged funds, asset managers, and other futures users.",
          frequency: "Weekly",
          publishTiming: "Friday for Tuesday positions",
          use: "Shows whether the basis trade or a directional futures position is crowded.",
          gap: "Too slow for live basis turns, but useful for identifying a crowded background.",
          link: "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"
        },
        {
          source: "FINRA Treasury trade transparency",
          description:
            "Next-day cash Treasury transaction activity for benchmark issues.",
          frequency: "Daily",
          publishTiming: "Following market day",
          use: "Lets you compare the futures story with the cash bond that should be moving with it.",
          gap: "You still do not get the full intraday futures-cash hedge mechanics that a basis desk sees.",
          link: "https://www.finra.org/finra-data/fixed-income/about-treasuries"
        },
        {
          source: "New York Fed and OFR funding data",
          description:
            "Broad secured funding and repo benchmarks needed to frame the financing side of the basis.",
          frequency: "Daily",
          publishTiming: "Business-day publication cycles",
          use: "Helps judge whether a basis move is really a financing story.",
          gap: "Broad repo is not the same thing as the exact financing available against the CTD on the desk.",
          link: "https://www.newyorkfed.org/markets/reference-rates"
        }
      ],
      researchUse:
        "Treat the basis as a hidden translation layer between macro and market structure. If the curve move sits inside a distorted futures-cash relationship, be careful about reading it as a pure regime repricing."
    },
    {
      id: "on-the-run-richness",
      number: "3",
      title: "On-the-run versus off-the-run richness",
      strapline: "When benchmark liquidity itself becomes a pricing factor.",
      deskSpeed: "Daily to weekly",
      publicRhythm: "Daily ex-post is possible; live depth is limited",
      definition:
        "On-the-run Treasuries are the newest benchmark issues at each maturity. They usually trade at richer prices and lower yields than older, similar bonds because they are more liquid, easier to hedge, and often more useful as collateral. Off-the-run bonds are older issues that can trade cheaper even when the macro picture has not changed.",
      whyDeskCares:
        "A desk must know whether a curve move is a true maturity-sector repricing or just a benchmark-liquidity effect. Richness or cheapness around benchmark rolls can create noise in the visible curve.",
      implications: [
        "The published yield curve can understate how cheap older securities really are.",
        "A sharp benchmark richness move may say more about collateral demand and liquidity preference than about macro expectations.",
        "Switch trades between neighboring issues become more active around new auctions and benchmark rollovers."
      ],
      terminology: [
        {
          term: "On-the-run",
          meaning:
            "The newest benchmark Treasury issue at a given maturity sector.",
          deskRead:
            "This is the most liquid reference bond and often the one most heavily used in hedging and pricing."
        },
        {
          term: "Off-the-run",
          meaning:
            "An older Treasury issue that is still outstanding but no longer the current benchmark.",
          deskRead:
            "It can be economically similar but less liquid and less prized as collateral."
        },
        {
          term: "Richness",
          meaning:
            "A bond trades at a higher price or lower yield than a comparable issue or fitted curve would suggest.",
          deskRead:
            "Investors are willing to pay up for liquidity, benchmark status, or collateral value."
        },
        {
          term: "Cheapness",
          meaning:
            "A bond trades at a lower price or higher yield than peers or a fitted curve imply.",
          deskRead:
            "The market needs compensation to hold a less liquid or less desirable issue."
        }
      ],
      deskVariables: [
        {
          name: "CUSIP-level yield spread",
          description:
            "The yield gap between the current benchmark bond and the nearest off-the-run issue.",
          whyItMatters:
            "This is the most direct measure of benchmark richness or off-the-run cheapness."
        },
        {
          name: "Bid-ask width and turnover",
          description:
            "How tightly the issue trades and how much volume goes through it.",
          whyItMatters:
            "Liquidity differences are one of the main reasons on-the-runs carry a premium."
        },
        {
          name: "Repo specialness of the benchmark issue",
          description:
            "Whether the benchmark bond is especially scarce as collateral in repo.",
          whyItMatters:
            "A very special benchmark often trades richer in cash too."
        },
        {
          name: "Switch spread across adjacent issues",
          description:
            "The relative spread between old and new benchmark issues when traders rotate from one to the other.",
          whyItMatters:
            "This is where benchmark roll effects become visible in practice."
        }
      ],
      publicInstruments: [
        {
          source: "Treasury auction results and auction history",
          description:
            "Official release history that identifies the newest benchmark securities and their terms.",
          frequency: "Event-driven with historical datasets",
          publishTiming: "Same day for auction results; ongoing historical access",
          use: "Lets you identify which CUSIP is on-the-run and when the benchmark changed.",
          gap: "Great for identification, but not enough by itself to measure live richness.",
          link: "https://www.treasurydirect.gov/auctions/announcements-data-results/announcement-results-press-releases/auction-results/"
        },
        {
          source: "FINRA Treasury transparency data",
          description:
            "End-of-day transaction reporting for benchmark Treasury trading.",
          frequency: "Daily",
          publishTiming: "Following morning",
          use: "Supports ex-post study of benchmark turnover and relative trade intensity.",
          gap: "Public users do not see live depth, dealer axes, or RFQ behavior that makes richness obvious on desks.",
          link: "https://www.finra.org/finra-data/fixed-income/about-treasuries"
        },
        {
          source: "FRED constant maturity series",
          description:
            "Institutionally fitted Treasury yield points rather than exact CUSIP quotes.",
          frequency: "Daily",
          publishTiming: "Business-day releases with timestamps by series",
          use: "Provides the visible benchmark curve that off-the-run bonds can deviate from.",
          gap: "It smooths the CUSIP-level richness that desks care about.",
          link: "https://fred.stlouisfed.org/"
        }
      ],
      researchUse:
        "When you see a sector move, ask whether it is a true maturity repricing or a benchmark liquidity event. On-the-run richness can make the visible curve look cleaner than the underlying cash market really is."
    },
    {
      id: "repo-specials",
      number: "4",
      title: "Repo specials",
      strapline: "When one Treasury issue becomes scarce collateral.",
      deskSpeed: "Intraday to daily",
      publicRhythm: "Daily broad funding only; true specials are mostly hidden",
      definition:
        "A Treasury goes special in repo when market participants are willing to lend cash at an unusually low rate just to borrow that specific bond as collateral. Specialness is a scarcity signal. It often reflects short-covering demand, delivery needs, benchmark scarcity, or basis-trade pressure.",
      whyDeskCares:
        "Repo specials tell you when a bond's collateral value is driving cash-market pricing. A bond can look rich not because macro investors love it, but because the market urgently needs that exact security.",
      implications: [
        "Cash-market richness can be partly collateral-driven rather than macro-driven.",
        "Futures delivery pressure can spill into repo specialness and then into cash prices.",
        "Specialness often reveals hidden stress earlier than the visible yield curve does."
      ],
      terminology: [
        {
          term: "General collateral (GC)",
          meaning:
            "The broad repo financing rate for standard Treasury collateral rather than a scarce specific issue.",
          deskRead:
            "This is the baseline funding level from which specialness is measured."
        },
        {
          term: "Special",
          meaning:
            "A security-specific repo rate that trades below the general collateral rate because the bond is scarce.",
          deskRead:
            "The market is paying up in financing terms to get hold of that particular CUSIP."
        },
        {
          term: "Special spread",
          meaning:
            "The gap between the general collateral rate and the issue-specific repo rate.",
          deskRead:
            "A larger spread usually means a more severe scarcity signal."
        },
        {
          term: "Fails",
          meaning:
            "Settlement failures in which a security is not delivered when expected.",
          deskRead:
            "Persistent fails can signal collateral scarcity or stressed market functioning."
        }
      ],
      deskVariables: [
        {
          name: "Specific-issue repo rate",
          description:
            "The financing rate against the exact Treasury issue a desk wants to borrow.",
          whyItMatters:
            "This is the direct measure of whether the bond is special."
        },
        {
          name: "GC repo rate",
          description:
            "The broad financing rate for standard Treasury collateral.",
          whyItMatters:
            "It is the baseline needed to calculate the size of the specialness gap."
        },
        {
          name: "Fails-to-deliver",
          description:
            "The amount of securities that were supposed to settle but did not.",
          whyItMatters:
            "Large or persistent fails often confirm real collateral scarcity."
        },
        {
          name: "Benchmark collateral demand",
          description:
            "Desk color on how strongly participants need one issue for hedging, settlement, or delivery.",
          whyItMatters:
            "This gives context that a public GC series cannot show."
        }
      ],
      publicInstruments: [
        {
          source: "New York Fed SOFR / TGCR / BGCR",
          description:
            "Official broad repo rates that give the general funding environment.",
          frequency: "Daily business days",
          publishTiming: "Morning publication",
          use: "Useful for broad funding conditions and the general collateral backdrop.",
          gap: "They do not reveal which exact Treasury issue is special, only the market-wide baseline.",
          link: "https://www.newyorkfed.org/markets/reference-rates"
        },
        {
          source: "OFR Short-Term Funding Monitor",
          description:
            "Public aggregate funding-monitoring data across repo segments.",
          frequency: "Daily refresh for many series",
          publishTiming: "Weekday refresh cycle",
          use: "Improves the broad funding and collateral context.",
          gap: "Still too broad to replace CUSIP-level specials data used on desks.",
          link: "https://www.financialresearch.gov/short-term-funding-monitor/api/"
        },
        {
          source: "Treasury and FINRA benchmark trading data",
          description:
            "Ex-post market activity in the benchmark issues that often go special.",
          frequency: "Daily and event-driven",
          publishTiming: "Next day or same-day event release",
          use: "Helps infer whether a benchmark richness move likely had collateral demand behind it.",
          gap: "You can infer specialness pressure, but you cannot observe the exact special rate directly from these sources.",
          link: "https://www.finra.org/finra-data/fixed-income/about-treasuries"
        }
      ],
      researchUse:
        "With public data, repo specials are mostly an inferred layer. Use them as a caution flag: if a benchmark issue looks too rich, ask whether collateral scarcity rather than macro conviction is driving it."
    },
    {
      id: "auction-microstructure",
      number: "5",
      title: "Auction microstructure",
      strapline: "How new Treasury supply is priced, absorbed, and judged.",
      deskSpeed: "Event-driven within minutes to days",
      publicRhythm: "Same-day event results with strong ex-post value",
      definition:
        "Auction microstructure is the internal demand story of a Treasury auction: what yield concession the market demanded beforehand, how the stop-out compared with the when-issued level, who absorbed the issue, and how the new bond traded immediately afterward.",
      whyDeskCares:
        "Treasury auctions are one of the cleanest public windows into supply-demand balance. They can reveal when the market is comfortable funding the government and when it is starting to require a fiscal premium or balance-sheet concession.",
      implications: [
        "A weak auction can cheapen a sector even if macro data were quiet.",
        "Repeated tails across a maturity sector can change how strategists read the long-end regime path.",
        "Auction digestion helps separate a true structural supply problem from a one-off timing problem."
      ],
      terminology: [
        {
          term: "When-issued",
          meaning:
            "The forward trading level of a Treasury issue before the auction settles.",
          deskRead:
            "This is the market's live expectation of where the new bond should clear."
        },
        {
          term: "Tail",
          meaning:
            "The auction stop-out yield is higher than the when-issued yield just before the sale.",
          deskRead:
            "Demand was weaker than expected, so the Treasury had to pay more."
        },
        {
          term: "Stop-through",
          meaning:
            "The auction stop-out yield is below the when-issued yield.",
          deskRead:
            "Demand was stronger than expected and the market cleared through its expected price."
        },
        {
          term: "Bid-to-cover",
          meaning:
            "Total bids received divided by the amount offered.",
          deskRead:
            "A high ratio usually signals stronger headline demand, though composition still matters."
        }
      ],
      deskVariables: [
        {
          name: "When-issued yield",
          description:
            "The market's pre-auction forward yield for the new security.",
          whyItMatters:
            "It is the reference point for judging whether the auction tailed or stopped through."
        },
        {
          name: "Tail or stop-through size",
          description:
            "The basis-point difference between stop-out and the pre-auction when-issued level.",
          whyItMatters:
            "This is one of the cleanest measures of auction strength or weakness."
        },
        {
          name: "Direct, indirect, and dealer allotment",
          description:
            "Which buyer group absorbed the issue at auction.",
          whyItMatters:
            "Dealer-heavy take-down can mean the real-money handoff was not strong enough."
        },
        {
          name: "Post-auction performance",
          description:
            "How the bond trades in the minutes, hours, and next day after the sale.",
          whyItMatters:
            "Good auctions can still lead to weak trading if the market struggles to digest the supply."
        }
      ],
      publicInstruments: [
        {
          source: "TreasuryDirect auction results",
          description:
            "Official same-day auction result pages and press releases.",
          frequency: "Event-driven",
          publishTiming: "Immediately after each auction result",
          use: "Essential for tails, stop-throughs, bid-to-cover, and headline allotment composition.",
          gap: "Very strong ex-post auction data, but not a live order-book or dealer color feed.",
          link: "https://www.treasurydirect.gov/auctions/announcements-data-results/announcement-results-press-releases/auction-results/"
        },
        {
          source: "Treasury Fiscal Data auction dataset",
          description:
            "Structured historical Treasury auction data via a public API and downloadable files.",
          frequency: "Historical dataset with ongoing updates",
          publishTiming: "Updated as auction history extends",
          use: "Perfect for backtesting sector tails, demand composition, and recurring auction patterns.",
          gap: "Historical and structured, but not enough by itself for intraday digestion analysis.",
          link: "https://fiscaldata.treasury.gov/api-documentation/"
        },
        {
          source: "Treasury investor-class allotments",
          description:
            "Public split of auction awards by investor category.",
          frequency: "Auction/event-driven",
          publishTiming: "Published with or around auction reporting",
          use: "Shows whether dealers, indirects, or directs carried the issue.",
          gap: "Still not the same as seeing live demand tone before the auction closes.",
          link: "https://home.treasury.gov/policy-issues/financing-the-government/treasury-investor-data"
        }
      ],
      researchUse:
        "Auction microstructure is one of the best public hidden-layer tools you have. Use it aggressively, but do not confuse one weak auction with a structural fiscal-dominance regime unless the pattern persists."
    },
    {
      id: "intraday-hedging-flow",
      number: "6",
      title: "Intraday hedging flow",
      strapline: "The Treasury move created by hedgers, not just macro investors.",
      deskSpeed: "Minutes to hours",
      publicRhythm: "Mostly inferred; direct public visibility is weak",
      definition:
        "Intraday hedging flow is the buying or selling generated by participants adjusting risk mechanically rather than expressing a pure macro view. This includes mortgage convexity hedging, dealer hedging, options-related flow, CTA trend-following, and stop-loss cascades.",
      whyDeskCares:
        "A sharp intraday move can look like a new macro regime when it is actually a self-reinforcing hedging process. Desks need to know whether the market is pricing information or amplifying it mechanically.",
      implications: [
        "Large yield moves can continue after the initial news shock because risk systems force more hedging.",
        "The belly or long end can move much more than the macro story alone would imply.",
        "Volatility itself becomes an input into more trading, which can make price action look nonlinear."
      ],
      terminology: [
        {
          term: "Convexity hedging",
          meaning:
            "Mortgage or options-related hedging that forces participants to buy or sell duration as yields move.",
          deskRead:
            "The market is not just reacting to news; it is reacting to the last move in yields."
        },
        {
          term: "Gamma hedging",
          meaning:
            "Options dealers adjust their hedges as the underlying market moves and option sensitivity changes.",
          deskRead:
            "Dealer hedging can either dampen or amplify the Treasury move."
        },
        {
          term: "CTA flow",
          meaning:
            "Trend-following systematic strategies that add to a move once price thresholds are crossed.",
          deskRead:
            "A macro move can accelerate mechanically if the price action itself triggers systematic selling or buying."
        },
        {
          term: "Stop-out cascade",
          meaning:
            "A chain of forced exits after positions breach risk or stop-loss thresholds.",
          deskRead:
            "The market starts repricing because other traders are being forced to move."
        }
      ],
      deskVariables: [
        {
          name: "Intraday futures depth and order-book imbalance",
          description:
            "How much size sits on the bid and offer and whether aggressive flow is one-sided.",
          whyItMatters:
            "This is where desks see whether a move is information-driven or mechanically forced."
        },
        {
          name: "Options gamma and convexity estimates",
          description:
            "Measures of how much hedging pressure is likely as rates move through certain levels.",
          whyItMatters:
            "These help predict when a move may accelerate for non-fundamental reasons."
        },
        {
          name: "Time-of-day volume pattern",
          description:
            "Where the move happens during the trading session and whether volume clusters around risk events.",
          whyItMatters:
            "A flow-driven move often has a very different time signature from a slow macro repricing."
        },
        {
          name: "Realized versus implied volatility",
          description:
            "Whether actual intraday movement is outrunning what options markets had priced.",
          whyItMatters:
            "This is often where forced hedging begins to matter."
        }
      ],
      publicInstruments: [
        {
          source: "CME volume and open interest summaries",
          description:
            "Public exchange-level context for Treasury futures trading activity.",
          frequency: "Daily for usable public summaries; more frequent with paid access",
          publishTiming: "Exchange publication cycle",
          use: "Helpful for seeing whether a move occurred in unusually heavy futures activity.",
          gap: "Does not replace a live order book or dealer gamma map.",
          link: "https://www.cmegroup.com/markets/interest-rates/us-treasury.html"
        },
        {
          source: "CFTC positioning data",
          description:
            "Weekly positioning in rates futures by broad participant category.",
          frequency: "Weekly",
          publishTiming: "Friday for Tuesday positions",
          use: "Background crowding context for whether flow squeezes are plausible.",
          gap: "Far too slow for actual intraday hedging analysis.",
          link: "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"
        },
        {
          source: "Daily realized moves in Treasury yields and MOVE-style vol proxies",
          description:
            "End-of-day measurement of how large the move actually was relative to the recent volatility backdrop.",
          frequency: "Daily",
          publishTiming: "Next-day via public market series",
          use: "Lets you infer whether the day likely involved mechanical flow amplification.",
          gap: "Inference only. Public users do not observe the intraday hedging engine directly.",
          link: "https://fred.stlouisfed.org/"
        }
      ],
      researchUse:
        "Use intraday hedging flow as a humility layer. When the move is too violent for the macro news alone, mark the day as mechanically amplified rather than automatically rewriting the regime."
    },
    {
      id: "positioning-stress",
      number: "7",
      title: "Positioning stress",
      strapline: "When the market is crowded enough that small shocks cause outsized moves.",
      deskSpeed: "Daily to weekly, but can break intraday",
      publicRhythm: "Weekly with daily inference",
      definition:
        "Positioning stress means the market has accumulated enough one-sided risk that a modest surprise can trigger outsized repricing. A crowded short can squeeze higher, a crowded long can flush lower, and a levered basis position can turn into a forced unwind.",
      whyDeskCares:
        "Positioning often explains why the same macro surprise produces a tiny move one month and a huge move another month. The regime message of a move cannot be read correctly without some sense of how crowded the street already was.",
      implications: [
        "Price action can overshoot the underlying macro information.",
        "Stop-loss cascades and VaR de-risking can turn a normal surprise into a disorderly session.",
        "A market can look fundamentally right in medium horizon terms but still be very unstable in the short term."
      ],
      terminology: [
        {
          term: "Crowded long / crowded short",
          meaning:
            "Too many participants are leaning in the same direction.",
          deskRead:
            "The next surprise can force many of them to move at once."
        },
        {
          term: "Squeeze",
          meaning:
            "A market move that accelerates because participants on the wrong side are forced to cover.",
          deskRead:
            "Positioning, not just information, is now driving price action."
        },
        {
          term: "VaR unwind",
          meaning:
            "Risk systems force position reduction because volatility or losses have risen too far.",
          deskRead:
            "The market is repricing because internal limits are being hit."
        },
        {
          term: "Basis leverage",
          meaning:
            "Leveraged use of the futures-cash basis trade, often financed in repo.",
          deskRead:
            "A basis unwind can look like a macro move even when it is really a leverage event."
        }
      ],
      deskVariables: [
        {
          name: "CFTC participant positioning",
          description:
            "Broad futures positions by leveraged funds, asset managers, and others.",
          whyItMatters:
            "This is the public starting point for judging whether a trade is crowded."
        },
        {
          name: "Open interest and options skew",
          description:
            "Contract participation and asymmetry in options demand.",
          whyItMatters:
            "These help identify whether downside or upside protection is concentrated."
        },
        {
          name: "Dealer inventory and balance-sheet strain",
          description:
            "How much risk intermediaries are already carrying alongside client flow.",
          whyItMatters:
            "Crowding becomes more dangerous when dealer capacity is already tight."
        },
        {
          name: "Cross-asset correlation breaks",
          description:
            "Situations where Treasuries stop behaving in their usual relation to equities, FX, or vol.",
          whyItMatters:
            "Correlation breaks often reveal stress and forced repositioning."
        }
      ],
      publicInstruments: [
        {
          source: "CFTC Commitments of Traders",
          description:
            "Official weekly positioning data across futures participant categories.",
          frequency: "Weekly",
          publishTiming: "Friday for Tuesday positions",
          use: "Best public gauge of broad rates positioning and crowding.",
          gap: "Too slow and too aggregated to capture live desk concentration or exact stop levels.",
          link: "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"
        },
        {
          source: "CME open interest and futures summaries",
          description:
            "Public participation and contract activity data for Treasury futures.",
          frequency: "Daily",
          publishTiming: "Exchange publication cycle",
          use: "Adds scale and change information around crowding conditions.",
          gap: "Useful context, but not a substitute for desk-level client concentration data.",
          link: "https://www.cmegroup.com/markets/interest-rates/us-treasury.html"
        },
        {
          source: "New York Fed Primary Dealer Statistics",
          description:
            "Weekly inventory and financing context for the dealer side of crowded positioning.",
          frequency: "Weekly",
          publishTiming: "Thursdays for the prior week",
          use: "Confirms whether crowding sits on a stressed intermediary base.",
          gap: "Slow and aggregated, but still valuable as a confirmation layer.",
          link: "https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics"
        }
      ],
      researchUse:
        "Use positioning stress to control your confidence. If the regime call seems right but the market move is outsized, ask whether crowding and forced flow made the short-horizon signal noisier than the medium-horizon story."
    }
  ]
};
