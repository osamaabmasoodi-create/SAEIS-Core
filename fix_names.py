import re

p = "/home/ubuntu/saeis_cost_structure_dashboard/client/src/pages/Home.tsx"
s = open(p).read()

# Fix trpc.xxx.yyy -> trpc.saeis.xxx.yyy for the SAEIS routers
for name in ["seed", "alerts", "erpRecords", "bankRecords", "matches", "dashboard"]:
    # only when followed by a dot then a method (not already prefixed)
    s = re.sub(rf"trpc\.(?!saeis){name}\.", rf"trpc.saeis.{name}.", s)

open(p, "w").write(s)
print("patched Home.tsx")
