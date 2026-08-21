# A skill file that exists and does not carry the rule

This fixture reproduces IMP-0140 exactly. The file EXISTS — which is all the improvement
agent checked before marking IMP-0111 APPLIED — and it does not contain the rule the log
entry claims it carries. The needle the fixture greps for is deliberately absent.
