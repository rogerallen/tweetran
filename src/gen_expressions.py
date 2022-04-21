#!/usr/bin/python3
# Get data from term-fns, unary-fns, etc. here:
# https://github.com/rogerallen/tweegeemee/blob/master/src/tweegeemee/image.clj
#
term_vals = """pos TAU PI""".split()
term_fns = """noise `snoise `plasma `splasma
                   `vnoise `vsnoise `vplasma `vsplasma
                   `grain `turbulence `vturbulence
                   `spots `blotches `agate `clouds `velvet `flecks `wood""".split()
unary_fns = """`vsin `vcos `vabs `vround `vfloor `vfrac
                   `square `vsqrt `sigmoid `triangle-wave `max-component `min-component
                   `length `normalize `gradient
                   `theta `radius `polar `height `height-normal
                   `hue-from-rgb `lightness-from-rgb `saturation-from-rgb
                   `hsl-from-rgb `red-from-hsl `green-from-hsl `blue-from-hsl
                   `rgb-from-hsl `x `y `z `t `alpha""".split()
binary_fns = """`v+ `v* `v- `vdivide `vpow `vmod `dot `cross3
                   `vmin `vmax `turbulate `checker `rotate `scale `offset
                   `adjust-hue `adjust-hsl `vconcat `average""".split()
ternary_fns = """`lerp `clamp `vif""".split() # `vconcat, `average can also be ternary
modpos_unary_fns = """`gradient""".split()
modpos_binary_fns = """`rotate `scale `offset""".split()

term_fns = [x.replace('`','') for x in term_fns]
unary_fns = [x.replace('`','') for x in unary_fns]
binary_fns = [x.replace('`','') for x in binary_fns]
ternary_fns = [x.replace('`','') for x in ternary_fns]
modpos_binary_fns = [x.replace('`','') for x in modpos_binary_fns]
term_fns.sort()
unary_fns.sort()
binary_fns.sort()
ternary_fns.sort()

def fixname(n):
    return f.replace('+','add')\
        .replace('v-','vsub')\
        .replace('length','vlength')\
        .replace('normalize','vnormalize')\
        .replace('dot','vdot')\
        .replace('clamp','vclamp')\
        .replace('*','mul')\
        .replace('-','_')

fn_db = {}
for f in term_fns:
    fn_db[f] = {'name':fixname(f), 'args':1, 'addpos': True, 'modpos': False}
for f in unary_fns:
    fn_db[f] = {'name':fixname(f), 'args':1, 'addpos': False, 'modpos': False}
for f in binary_fns:
    fn_db[f] = {'name':fixname(f), 'args':2, 'addpos': False, 'modpos': False}
for f in ternary_fns:
    fn_db[f] = {'name':fixname(f), 'args':3, 'addpos': False, 'modpos': False}
fn_db['checker']['addpos'] = True
fn_db['turbulate']['addpos'] = True
fn_db['turbulate']['modpos'] = True
fn_db['gradient']['addpos'] = True
fn_db['gradient']['modpos'] = True
for f in modpos_binary_fns:
    fn_db[f]['addpos'] = True
    fn_db[f]['modpos'] = True

# output headers
print("// AUTOMATICALLY GENERATED FILE.  DO NOT EDIT")
print("// Created by gen_expressions.py script")
print("static std::map<std::string, std::string> gFunctionRename = {")
for k in fn_db.keys():
    print("    {\"%s\", \"%s\"},"%(k,fn_db[k]["name"]))
print("};")
print()

# we don't use this any longer
#print("static std::map<std::string, int> gFunctionToNumArgs = {")
#for k in fn_db.keys():
#    print("    {\"%s\", %d},"%(k,fn_db[k]["args"]))
#print("};")
#print()

print("static std::set<std::string> gAddPos = {")
for k in fn_db.keys():
    if fn_db[k]["addpos"] == True:
        print("    \"%s\","%(k))
print("};")
print()

print("static std::set<std::string> gModPos = {")
for k in fn_db.keys():
    if fn_db[k]["modpos"] == True:
        print("    \"%s\","%(k))
print("};")
print()

# unused
#print("static std::set<std::string> gTermVals = {")
#for k in term_vals:
#    print("    \"%s\","%(k))
#print("};")
#print()

print("static std::set<std::string> gTermFns = {")
for k in term_fns:
    print("    \"%s\","%(k))
print("};")
print()