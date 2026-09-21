import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ---------------------------------------------------------
# 1. إعدادات الصفحة والشعار المدمج المباشر
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & Intelligence System",
    page_icon="🛡️",
    layout="wide"
)

# الشعار الرسمي الصريح بنظام PNG Base64
SAEIS_LOGO_B64 = """
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/D/32S/7f8fC5xzeee3I2yA4+eO83v/Ivn791e8XvSfpH+5a49L4A6oM3S6i93+z+6T23vvPnPnf5/Lmt51111m3PP331fXvf8/Svf2ftG//oQ784MDTcv2nrU4/e/yC+D/A6Dk10X9EIsyKz6T4k8yv/2A/f01t48Y8e2vjUj3pXbXl+/X33PrZxzW89eM+93/3i333y4sWL3vy29/3s+g3rn2876mE+4zITh1i34Pxf/st931+R/drX3veffnnF8oXf//KffubmX3/3I1v2fvy33/e1rYPrHnvy2d/6lS/es27v4f25/eP/mU168+2/eMevfv1p/e98+A//8vXnv/k97/vwnkfvumf1m/937//89XdfseLSN3zszs8/snZf3+f++09+23EseS5gxmTWf//+D/+Pv33Xb170+Gff+98fvfN/Pf4A29f/15Nf/vE3v/z5O3d3XfS53/+p2++6ef/O+/Y8+9gBfB900kS4L4k6hL/63N9e8v5XnN2y7rM3fv2+d/zpl6742aO73/m/3/xft/7G6xavfce97/1vf3D1i310rn/oF/e9y1+f9rLpA71I53+/5eO/ev+X/4933Hzn1s/84x2/3vvu2++//I4vXnfuG86/7+77373/3T+86xf+a3D//mefeuaxA+T2oM6dC2SWh9a/vO/Wv3vXz5zftXvH6v97+X//rxe+9OOHm+8/9d5/9cMnv3b99l3H65f8SJD5rT+85523PXXj7be3m13f/+i/vf8L9z8Kff/u0R++/o1PfmrtQ3fceft/uOnzH9ly669t/P5/3fn80f+Xp4A9f/21O//ititP2vL0Y//22y97/mPvXbN1361/8r3PfuGf/9/7Nu4++MOnYV6b3y44Xp05M3113q/4i0/fufG2n/6Xtz04d6H7y0sXPfz1H2y+bfuO4x/e7Ssz4/u0qM6e39r9u5/74jduf4xXX33a6f/p9p33fe1H+5qj9X6P4lA//P6v/9Xm7Z/+p5tuOvf8b3z1P2/f4eCvfI/vT9K/E416m934Lh5v63q3L9x032N8+SufvmO/u+zK31i6eNef/9vPrmk9Yp1N2lmdc1vK125s4Ybbdr/nr992zZf+/Xuv+/N33fr3e/q6O9s6v/u1/37X2pfe9s2/2jX/Hde/6v2v7fv9L3x108sP8+BTT/B3f38rZqijpTq48yAOfP3m1/0v56x8+G+/fve+y9516zlnv21R0Ld72/33PPzI/k0f/9O/72s9/42f/p2/fX49j3/rt//l6Sfe9/Xv/M171/37+s4eCufRzIbgfO7+G+9+/x+dd+b6Zzbfet3rfvLut8/r33f92n133v34N//szpsO8m+9T3x2x1e2XHHpmy95w9+/8M/fuPl9X21d/C992//2r/3h73S9s2sXv0jA/P4677A23i7vfvBfvvLZbzyy9k333P/o91ff/q/f6b3o3fS//09ffvC21fXv6r38s/Nee60bvv3Oq7a/2v3/e6+bT14oZNZv4tC2b/3zS+a/s2/x8I0ffmDXp269a8mbb/7Uay+81C1//iSfvPP23S239m96f9f3XvfP61//8e833//o9f/X9uXf77/ilq19q5//8UfOa124uOW0V8xbd/0//f8fu35b0d0T3/I//xTeeetq77r5U+f91iO7b/nmfe49e+f86h3Xn3X+CbfctfqeO37ymd5/233XW97/zXed9pufW3v7p/711y/Nfe8jS+/7f9p338kLhcyi2/z9/33i5T9q3fnE1/5292398939X/nhvU8uX335q49kU3L45CfeSObP54a4a8/q1S9937dvedNfP/qO97+/9X/duvbWW/33qfT3m4+/o6/lXevfe/V1f/j3l374i2vu33L4aA3/9jE9v//XW+6b3+r4gfe23fnMxttfeM/N73nly33lH9pW3/6eB54/3d1003V9C4fO/bE040p1qI+zXyYk3336U/ffcOPf/e1Pfn1u69o3Pve9x/ee8e5PvX/Dly7Y1Xb2S3e/7s2f/e5PPrs2f/iI2vL7v/SZT448f8Pvf+/W73y6t/m42q72m2+9/uMbfvh5T3LzTf/7jse8X/f6C884iYv48a0fWbr88itOW/Wv/e5+vU33f9U9qX/r/473vvY3vvKj1S98m4ff/qFvf63pD/pXX/T/1s4p1+S8f5SAnIrmz3x8Y3mYmGg4IBy4+c1bXvK7P7zhH9732fW/cv5pC444/S03/X3/419+94m/y+/jN36s4+uP/s0L37+tC/9jR65Lp2MceNIn/u+/O3fVqze43Svv/c0v8tbb3/09S5bM3S6+GvP+P79x6G8v6n38+49/fC9vv+vR2/e97jM/2fO5a9/50G23f/jFvN8qX051f+f/z0Imsx38jL939U3+Pbf851f//n89sf0dH2z9/Nfv+YevfufhVfS3L1q6p6f1/M0/6Xvfve/32x1/d8Xnv/7Mh/+m4Zq4H7mGv7rr8y996kX9b27b37f48bse2nL6jfev+uO/eOnP3X3p389df9W1/a5L1E22/2s48+wD81a629b3X/iFr/3jF1+v//02X249qZc6Xw7055OaZFYPj33x5g8u/Y01b+kZuvH/e+2Hk1v++xMv+733/87dF72t68xWf22mbfM+v2vN8P27D/S/Yt2L265uO93zZ214/19/dOXXf/S2nzt3SXP3+O016l1y810f+I2/fE3vxV943S0rt67f2feE7+m+oef5728aXfnh21b8y6d7yvS462++5s4lC/p29T55/x5m9c656dIjs6x++3M/e+jYqC6sP9/z7j+771NvXj1403/b/pEP3brmA43P/qfD0kU6e80b2r+95/D9d5d5/rG23s98yD/45/f0fv1Xb/vOvd//yX/uX738bL8f2m/a36Pevv2fWbn59S/67u0f/s8vf+m7W3+15cK2s2LceE9b/a3vv+L1t7z3vbe899brL3/j9Icf3L/i73/y+1/4qU13ff7820//pXvv+cItK/2/S4d23/eW1U8I03N10M9+mU3e7b/+2yvOf92a5/q7LnvoHbdse9O9N91+1d/3mPve+28P/eOlv1O5xS2XXb+5/3fved+/3fnhS96z6aWf3f+9V29at/6m+0998MefX1I43QG5049bNvd9/JbvXvm+L7zr/Wdf9+j3v/jLdz/0/k/f17H34euvW/fJNz12339d/l/9/f/43LdfduUnX7/2c7et/cCXb3f/4aX3/64/+u6f++x7n9/33Qee/vj6l3b/uG3f5s+uvf8zn1m76lP9i/v3+u63PveH193zN++5+13f/9K3vvGTr124eS8v/2fL+xO/8j/c9dOf99R15GjI1Lp306E/l/S/3r2+23a8080fH3B33Xbr888f+O01f7Puz9oX//yK/b39j229x3fse8x3vO4m3/P/9/1t634Ibd55xWc3L39h1e++e1e32fPAnf7vfv5m3/5zTf93rT94z4P3s3//pP6vX/zU2vtfqO/3u3Xl3b5n5br1j28l13fXg5tf5HneXff3O+/233zP2s3tX7zxz5v0U/4fbrtzf4+XN+y6+2m3f0fv04vI4c33vvx77X/mI7//sA/f5Aft3v+Ffe3ffcvz+v33mS/7mxf+/9t+6K+t29jbf+xrt27qG44d4i/1X4TfvuvbH2xfce3xI9N2P0q0l8g03/pX395z6i0331S84I1fvvn4a+vOfO0/fe31215+iHce2vL8vE+/5r4v/uL4s6599qUft9/1L9v7LnrbrZdf+rYrf+u0zS+u/f4/X3vdM+t39H3z+s1bv/P3H9jU8yvnrXzrG2664pLzX910yq4n7/+nP31f50ff/kO3XH/P//2+l243OxeftPL373vrxpefe+reW/pOfNufv/p/fv3Gq09a8f4vffb2p54+sA725S+c9+v3v+X+zde/e/3mbf1b1j19bseZX3nzmddcdv4F/c4f2Pn333xhy/O3f/q3n/iNDbftfOa+e27/53fd3PevO963s+/eD3zmF+evfv+1m34Wbvv0/1x49Rvu2j34l43P/Ew0sB3f990/ve3+E1/3nS/ddO43Pnn7227t//7f3f33m1Zfcv/tX3v3YzvW3XXHdz78vR3Xf+2+S25fe/363Vvuf3jr4/80MHT/x+/ffLz//c8fH+R/vv35i2s3PvG//9ePfXnrE/sObXrtO1/82qve8y/mrf6j/8e6G25615d/uOvj24a6T9vxx7d+s/j4v/7BqSvfddv7rvx0f2vv82t/evvvv+v53/zE2SvevGnrk5suftfnO1+85b3/3HHzL3S++Z1rFmxc19/73e++/s6mK/s3fXv33y1cecfHv/e+3y49vvbdq59Yd/tX7rtqwwuv3/S12y/s/XrfVbe889oLN//AHzj7rIduvvuB5//zR898t3mQ248yI/pE43d/P02mOfLwJm9wz95P/89v7rnur/+m669+c+kHvnvXFm9feMOf3/f4L17/+xfevvPqT92ycZpLp7e/sOGG537y63/z8f3X3/f/fP83m9b867fuWr+n87aPr3j3S2f2XfInX/v1Cza9cfvNl6966G9uX/3gD3q3/u3qT35+/f+3e8d/9x26sXfLzY++dM//3jZve/G8j86P+v4mN38zO/8f3vXU7y846x9+4drbrr72tS//k91vfu6qNfd/p++d6e6a0d3+f/PInXfsveS/feG2D43O/4trvv4fv56u5fE/f9m/fe93vvS39+69/b/Nf3v32xduvP013//m62+/c5vP/eC33v2/b1m31SfvI/f+4M/+vX/gmtuu/+jL13zx1m/s2fb/nnD2O2//5s/v/u1/63351i9/9+6n33Xf34QnvXv3r2++9m8/e1Xffbdv2fnfN/xGzy9+4o0/vef+0/qff4s99x41j9/0L/f56+e/5c63XfzWd2zc1j33t333v330p6978Yc3/OfX3/aKzfe/67pP/2fvt++8bM8Pf3fLffuOf+2f3nrf9a9578ef+X7o4p/400f/4t5/uv/2f534T+35a+vf/v019//Xv2q64s0/aP39/e3/33m463ev2/ytp3v+31tvu2731d/+ylp8uS738o1f+/Ztn/rC99b+R3/r5S+e98946f/1p/f9xf6P3Llh8f6bfvS12/vfcv6139/1gS/m7t+/12f5R96w+t4tX/7U53bsu2f3X2+5YdMv3v5/fe3aT7a8+/m3rtj1L2v2vf2G5/+6/1vf2XD32mff841/v6y741vfueX9N33z56t2r4aP/48pG+mI0YmX4E7cR/d890v/1S33vOb2d//xO//9x/9t9y1f3fyxL1/e3fH15d3fv/i3Pnv/y9uX3nr/79zzvTft+9qPdv/i2/7y4Lff3927dFvL6++54Uv/2nn6/3XWp++/5r86/61r598m5Xf03fW/S59/Yd/aT13/1mP2dHz6I5+92j/42e43//4N/2vtR5//51te3I4/sM9/aPPi9/z2q25qO+/GZ754S++2n3SdtvyNf3X9f33z3i03XnfX+s91fG5f5xtLnvja5q4v3fD4mve8952r33/1bdt+8f343v/9X7+35yv//k1fef7/4l//4x+3fH2s4/O3v3b18p/a097x+f93+ycf+7Uv/qD/D4e2v//b65/cceMft31s+aev+er9m96/9L+3vfvdr//+915/1vLqG/9l3de3f+zrv/q3y950xfL33P+f92/deP33f+d/rtvyxJ7bv/Xnrfcfv3T3q7++4Z6/Wfv1217+/O9se3f5m9//Xf/44vse2XzL4Xk5v1y4/aPvufzV513904cvvOiP/37v3e13ffrtd208q2XZlWf9z8/98J/ed9a2s992yxdvfMcf3PTm3u3/f/f69W87u9n4xM/+7O03PvGfXvK24U+tf33T51v8u3//tqf39226++b/tXj/4C98cv0n+l5f6l2wb8e2q5YseXz1k92Xf3TzNz/fdu7d598s636x5O9vvn3N4Xevvu/f96vP3fS+m/e1Pnr9/3/l2X+363u3vnT7/s9seG6ffuD1p330yv1bb/rnz//4zO/97O6/ee/qK/5w+y8u2fq16+69e83O3f2f/s5H153eueX419/5nTv3X3Xz29/eufm/Lrv3v919z+1vf92y5f/1m0+uvftf3vv5y/e+9PcfXP/tO29+z6q+O3+481O3/v673/T//d4133nnmSvuWP/1x/e3/OnqV/3+eT1vvv7fvvfBbf/x4GfWfG3L3I9ef9oV5y6/+P5PvfnL429f+/p3fvqJzW0X/eSsn4mXlPmnA1O6eJ/X5E9I32/2Xvv5/6i/839c894vvXf373XevX73zstOf2v/3O98df0n/mJ49+6PvG/12r+ve9e+V/9s1c7/uu817e4fPnLH9T/r8o5e/8j/+vM3vf343fXN23+x+uOnXpve+/n/cv9zX3/j/V/45K/3vP6y23e85e2/deN3vn3/1Zf94f997+f33fX4bbf94A1Xb/z2H932xft3PPXfT3/b4d6/aLrz+6svfvN9v//3b3jrq27d88rPvfX1a2/e8i/X/92G37zn5iuv33L3R1Y+/4X3f/p2+97O4qP3v+Nrf3P9xRfd/+7Pfu/ebzS71+3o/9wL7//74/Z9+v0fnLvy/B//53tv/I0br1v3iRve8o7V/3XnB2+7+/Nnv6XlS/3f+XTH8/vef+0pG3v/q3d49e6f/I+/P+3Vb/v2T980vOuK1eefee+G+y945f3//Z9mve5f+/a/+e3G9r/42y/d/4sfrn3d6cddduv4zV+m9/jOni/++4dPPXX1mR+d91/euf/L39i89Y6u3m+X/qOxe/2B4675H376aEunX/Xo7k5/40U9S/7m85/f8/Fbfve6q756zztf1fXf/u5vfuaq+b/c88C/vuvfPnX52a/v+O3f++e/6Ln7fT3Hq//mJ9/49A9+snX9Z5/+7Y+sWPWjS7783u+ve+4vvveprVd+9Z6ffs/f/2/9a1/14Xte/8W2z9+9Z8v/+I3jHv7Mv/zpZ9/7O7esWXXvE/e/64v3Pf/03e+44eOP3b355qUrv3vfT9+x4L8+seS2P3nLDTd/43OP3PTYqltvuO2/fGf7C//iX33mO6//3o3nPfv477/iyt3fece/f/K/7XjX/I+0vvf3V3/4y++//fM33XjX/Xf33Pqjtz580+33f+vA+Z+9o3+3s/7Wk43425f38q3v/S833/23N39x9ed/d/vjN6z89bO333rtvT96+L61d3//o8+1d/ztR14/vPXv19y+Ycct3161c+sn3/35l77/4a1f+cO43v/53b+665sX9f7f45778a+t/d0P/st/Wf/jP2p338kLhcyi2/z9/33i5T9q3fnE1/5292398939X/nhvU8uX335q49kU3L45CfeSObP54a4a8/q1S9937dvedNfP/qO97+/9X/duvbWW/33qfT3m4+/o6/lXevfe/V1f/j3l374i2vu33L4aA3/9jE9v//XW+6b3+r4gfe23fnMxttfeM/N73nly33lH9pW3/6eB54/3d1003V9C4fO/bE040p1qI+zXyYk3336U/ffcOPf/e1Pfn1u69o3Pve9x/ee8e5PvX/Dly7Y1Xb2S3e/7s2f/e5PPrs2f/iI2vL7v/SZT448f8Pvf+/W73y6t/m42q72m2+9/uMbfvh5T3LzTf/7jse8X/f6C884iYv48a0fWbr88itOW/Wv/e5+vU33f9U9qX/r/473vvY3vvKj1S98m4ff/qFvf63pD/pXX/T/1s4p1+S8f5SAnIrmz3x8Y3mYmGg4IBy4+c1bXvK7P7zhH9732fW/cv5pC444/S03/X3/419+94m/y+/jN36s4+uP/s0L37+tC/9jR65Lp2MceNIn/u+/O3fVqze43Svv/c0v8tbb3/09S5bM3S6+GvP+P79x6G8v6n38+49/fC9vv+vR2/e97jM/2fO5a9/50G23f/jFvN8qX051f+f/z0Imsx38jL939U3+Pbf851f//n89sf0dH2z9/Nfv+YevfufhVfS3L1q6p6f1/M0/6Xvfve/32x1/d8Xnv/7Mh/+m4Zq4H7mGv7rr8y996kX9b27b37f48bse2nL6jfev+uO/eOnP3X3p389df9W1/a5L1E22/2s48+wD81a629b3X/iFr/3jF1+v//02X249qZc6Xw7055OaZFYPj33x5g8u/Y01b+kZuvH/e+2Hk1v++xMv+733/87dF72t68xWf22mbfM+v2vN8P27D/S/Yt2L265uO93zZ214/19/dOXXf/S2nzt3SXP3+O016l1y810f+I2/fE3vxV943S0rt67f2feE7+m+oef5728aXfnh21b8y6d7yvS462++5s4lC/p29T55/x5m9c656dIjs6x++3M/e+jYqC6sP9/z7j+771NvXj1403/b/pEP3brmA43P/qfD0kU6e80b2r+95/D9d5d5/rG23s98yD/45/f0fv1Xb/vOvd//yX/uX738bL8f2m/a36Pevv2fWbn59S/67u0f/s8vf+m7W3+15cK2s2LceE9b/a3vv+L1t7z3vbe899brL3/j9Icf3L/i73/y+1/4qU13ff7820//pXvv+cItK/2/S4d23/eW1U8I03N10M9+mU3e7b/+2yvOf92a5/q7LnvoHbdse9O9N91+1d/3mPve+28P/eOlv1O5xS2XXb+5/3fved+/3fnhS96z6aWf3f+9V29at/6m+0998MefX1I43QG5049bNvd9/JbvXvm+L7zr/Wdf9+j3v/jLdz/0/k/f17H34euvW/fJNz12339d/l/9/f/43LdfduUnX7/2c7et/cCXb3f/4aX3/64/+u6f++x7n9/33Qee/vj6l3b/uG3f5s+uvf8zn1m76lP9i/v3+u63PveH193zN++5+13f/9K3vvGTr124eS8v/2fL+xO/8j/c9dOf99R15GjI1Lp306E/l/S/3r2+23a8080fH3B33Xbr888f+O01f7Puz9oX//yK/b39j229x3fse8x3vO4m3/P/9/1t634Ibd55xWc3L39h1e++e1e32fPAnf7vfv5m3/5zTf93rT94z4P3s3//pP6vX/zU2vtfqO/3u3Xl3b5n5br1j28l13fXg5tf5HneXff3O+/233zP2s3tX7zxz5v0U/4fbrtzf4+XN+y6+2m3f0fv04vI4c33vvx77X/mI7//sA/f5Aft3v+Ffe3ffcvz+v33mS/7mxf+/9t+6K+t29jbf+xrt27qG44d4i/1X4TfvuvbH2xfce3xI9N2P0q0l8g03/pX395z6i0331S84I1fvvn4a+vOfO0/fe31215+iHce2vL8vE+/5r4v/uL4s6599qUft9/1L9v7LnrbrZdf+rYrf+u0zS+u/f4/X3vdM+t39H3z+s1bv/P3H9jU8yvnrXzrG2664pLzX910yq4n7/+nP31f50ff/kO3XH/P//2+l243OxeftPL373vrxpefe+reW/pOfNufv/p/fv3Gq09a8f4vffb2p54+sA725S+c9+v3v+X+zde/e/3mbf1b1j19bseZX3nzmddcdv4F/c4f2Pn333xhy/O3f/q3n/iNDbftfOa+e27/53fd3PevO963s+/eD3zmF+evfv+1m34Wbvv0/1x49Rvu2j34l43P/Ew0sB3f990/ve3+E1/3nS/ddO43Pnn7227t//7f3f33m1Zfcv/tX3v3YzvW3XXHdz78vR3Xf+2+S25fe/363Vvuf3jr4/80MHT/x+/ffLz//c8fH+R/vv35i2s3PvG//9ePfXnrE/sObXrtO1/82qve8y/mrf6j/8e6G25615d/uOvj24a6T9vxx7d+s/j4v/7BqSvfddv7rvx0f2vv82t/evvvv+v53/zE2SvevGnrk5suftfnO1+85b3/3HHzL3S++Z1rFmxc19/73e++/s6mK/s3fXv33y1cecfHv/e+3y49vvbdq59Yd/tX7rtqwwuv3/S12y/s/XrfVbe889oLN//AHzj7rIduvvuB5//zR898t3mQ248yI/pE43d/P02mOfLwJm9wz95P/89v7rnur/+m669+c+kHvnvXFm9feMOf3/f4L17/+xfevvPqT92ycZpLp7e/sOGG537y63/z8f3X3/f/fP83m9b867fuWr+n87aPr3j3S2f2XfInX/v1Cza9cfvNl6966G9uX/3gD3q3/u3qT35+/f+3e8d/9x26sXfLzY++dM//3jZve/G8j86P+v4mN38zO/8f3vXU7y846x9+4drbrr72tS//k91vfu6qNfd/p++d6e6a0d3+f/PInXfsveS/feG2D43O/4trvv4fv56u5fE/f9m/fe93vvS39+69/b/Nf3v32xduvP013//m62+/c5vP/eC33v2/b1m31SfvI/f+4M/+vX/gmtuu/+jL13zx1m/s2fb/nnD2O2//5s/v/u1/63351i9/9+6n33Xf34QnvXv3r2++9m8/e1Xffbdv2fnfN/xGzy9+4o0/vef+0/qff4s99x41j9/0L/f56+e/5c63XfzWd2zc1j33t333v330p6978Yc3/OfX3/aKzfe/67pP/2fvt++8bM8Pf3fLffuOf+2f3nrf9a9578ef+X7o4p/400f/4t5/uv/2f534T+35a+vf/v019//Xv2q64s0/aP39/e3/33m463ev2/ytp3v+31tvu2731d/+ylp8uS738o1f+/Ztn/rC99b+R3/r5S+e98946f/1p/f9xf6P3Llh8f6bfvS12/vfcv6139/1gS/m7t+/12f5R96w+t4tX/7U53bsu2f3X2+5YdMv3v5/fe3aT7a8+/m3rtj1L2v2vf2G5/+6/1vf2XD32mff841/v6y741vfueX9N33z56t2r4aP/48pG+mI0YmX4E7cR/d890v/1S33vOb2d//xO//9x/9t9y1f3fyxL1/e3fH15d3fv/i3Pnv/y9uX3nr/79zzvTft+9qPdv/i2/7y4Lff3927dFvL6++54Uv/2nn6/3XWp++/5r86/61r598m5Xf03fW/S59/Yd/aT13/1mP2dHz6I5+92j/42e43//4N/2vtR5//51te3I4/sM9/aPPi9/z2q25qO+/GZ754S++2n3SdtvyNf3X9f33z3i03XnfX+s91fG5f5xtLnvja5q4v3fD4mve8952r33/1bdt+8f343v/9X7+35yv//k1fef7/4l//4x+3fH2s4/O3v3b18p/a097x+f93+ycf+7Uv/qD/D4e2v//b65/cceMft31s+aev+er9m96/9L+3vfvdr//+915/1vLqG/9l3de3f+zrv/q3y950xfL33P+f92/deP33f+d/rtvyxJ7bv/Xnrfcfv3T3q7++4Z6/Wfv1217+/O9se3f5m9//Xf/44vse2XzL4Xk5v1y4/aPvufzV513904cvvOiP/37v3e13ffrtd208q2XZlWf9z8/98J/ed9a2s992yxdvfMcf3PTm3u3/f/f69W87u9n4xM/+7O03PvGfXvK24U+tf33T51v8u3//tqf39226++b/tXj/4C98cv0n+l5f6l2wb8e2q5YseXz1k92Xf3TzNz/fdu7d598s636x5O9vvn3N4Xevvu/f96vP3fS+m/e1Pnr9/3/l2X+363u3vnT7/s9seG6ffuD1p330yv1bb/rnz//4zO/97O6/ee/qK/5w+y8u2fq16+69e83O3f2f/s5H153eueX419/5nTv3X3Xz29/eufm/Lrv3v919z+1vf92y5f/1m0+uvftf3vv5y/e+9PcfXP/tO29+z6q+O3+481O3/v673/T//d4133nnmSvuWP/1x/e3/OnqV/3+eT1vvv7fvvfBbf/x4GfWfG3L3I9ef9oV5y6/+P5PvfnL429f+/p3fvqJzW0X/eSsn4mXlPmnA1O6eJ/X5E9I32/2Xvv5/6i/839c894vvXf373XevX73zstOf2v/3O98df0n/mJ49+6PvG/12r+ve9e+V/9s1c7/uu817e4fPnLH9T/r8o5e/8j/+vM3vf343fXN23+x+uOnXpve+/n/cv9zX3/j/V/45K/3vP6y23e85e2/deN3vn3/1Zf94f997+f33fX4bbf94A1Xb/z2H932xft3PPXfT3/b4d6/aLrz+6svfvN9v//3b3jrq27d88rPvfX1a2/e8i/X/92G37zn5iuv33L3R1Y+/4X3f/p2+97O4qP3v+Nrf3P9xRfd/+7Pfu/ebzS71+3o/9wL7//74/Z9+v0fnLvy/B//53tv/I0br1v3iRve8o7V/3XnB2+7+/Nnv6XlS/3f+XTH8/vef+0pG3v/q3d49e6f/I+/P+3Vb/v2T980vOuK1eefee+G+y945f3//Z9mve5f+/a/+e3G9r/42y/d/4sfrn3d6cddduv4zV+m9/jOni/++4dPPXX1mR+d91/euf/L39i89Y6u3m+X/qOxe/2B4675H376aEunX/Xo7k5/40U9S/7m85/f8/Fbfve6q756zztf1fXf/u5vfuaq+b/c88C/vuvfPnX52a/v+O3f++e/6Ln7fT3Hq//mJ9/49A9+snX9Z5/+7Y+sWPWjS7783u+ve+4vvveprVd+9Z6ffs/f/2/9a1/14Xte/8W2z9+9Z8v/+I3jHv7Mv/zpZ9/7O7esWXXvE/e/64v3Pf/03e+44eOP3b355qUrv3vfT9+x4L8+seS2P3nLDTd/43OP3PTYqltvuO2/fGf7C//iX33mO6//3o3nPfv477/iyt3fece/f/K/7XjX/I+0vvf3V3/4y++//fM33XjX/Xf33Pqjtz580+33f+vA+Z+9o3+3s/7Wk43425f38q3v/S833/23N39x9ed/d/vjN6z89bO333rtvT96+L61d3//o8+1d/ztR14/vPXv19y+Ycct3161c+sn3/35l77/4a1f+cO43v/53b+665sX9f7f45778a+t/d0P/st/Wf/jP2p338kLhcyi2/z9/33i5T9q3fnE1/5292398939X/nhvU8uX335q49kU3L45CfeSObP54a4a8/q1S9937dvedNfP/qO97+/9X/duvbWW/33qfT3m4+/o6/lXevfe/V1f/j3l374i2vu33L4aA3/9jE9v//XW+6b3+r4gfe23fnMxttfeM/N73nly33lH9pW3/6eB54/3d1003V9C4fO/bE040p1qI+zXyYk3336U/ffcOPf/e1Pfn1u69o3Pve9x/ee8e5PvX/Dly7Y1Xb2S3e/7s2f/e5PPrs2f/iI2vL7v/SZT448f8Pvf+/W73y6t/m42q72m2+9/uMbfvh5T3LzTf/7jse8X/f6C884iYv48a0fWbr88itOW/Wv/e5+vU33f9U9qX/r/473vvY3vvKj1S98m4ff/qFvf63pD/pXX/T/1s4p1+S8f5SAnIrmz3x8Y3mYmGg4IBy4+c1bXvK7P7zhH9732fW/cv5pC444/S03/X3/419+94m/y+/jN36s4+uP/s0L37+tC/9jR65Lp2MceNIn/u+/O3fVqze43Svv/c0v8tbb3/09S5bM3S6+GvP+P79x6G8v6n38+49/fC9vv+vR2/e97jM/2fO5a9/50G23f/jFvN8qX051f+f/z0Imsx38jL939U3+Pbf851f//n89sf0dH2z9/Nfv+YevfufhVfS3L1q6p6f1/M0/6Xvfve/32x1/d8Xnv/7Mh/+m4Zq4H7mGv7rr8y996kX9b27b37f48bse2nL6jfev+uO/eOnP3X3p389df9W1/a5L1E22/2s48+wD81a629b3X/iFr/3jF1+v//02X249qZc6Xw7055OaZFYPj33x5g8u/Y01b+kZuvH/e+2Hk1v++xMv+733/87dF72t68xWf22mbfM+v2vN8P27D/S/Yt2L265uO93zZ214/19/dOXXf/S2nzt3SXP3+O016l1y810f+I2/fE3vxV943S0rt67f2feE7+m+oef5728aXfnh21b8y6d7yvS462++5s4lC/p29T55/x5m9c656dIjs6x++3M/e+jYqC6sP9/z7j+771NvXj1403/b/pEP3brmA43P/qfD0kU6e80b2r+95/D9d5d5/rG23s98yD/45/f0fv1Xb/vOvd//yX/uX738bL8f2m/a36Pevv2fWbn59S/67u0f/s8vf+m7W3+15cK2s2LceE9b/a3vv+L1t7z3vbe899brL3/j9Icf3L/i73/y+1/4qU13ff7820//pXvv+cItK/2/S4d23/eW1U8I03N10M9+mU3e7b/+2yvOf92a5/q7LnvoHbdse9O9N91+1d/3mPve+28P/eOlv1O5xS2XXb+5/3fved+/3fnhS96z6aWf3f+9V29at/6m+0998MefX1I43QG5049bNvd9/JbvXvm+L7zr/Wdf9+j3v/jLdz/0/k/f17H34euvW/fJNz12339d/l/9/f/43LdfduUnX7/2c7et/cCXb3f/4aX3/64/+u6f++x7n9/33Qee/vj6l3b/uG3f5s+uvf8zn1m76lP9i/v3+u63PveH193zN++5+13f/9K3vvGTr124eS8v/2fL+xO/8j/c9dOf99R15GjI1Lp306E/l/S/3r2+23a8080fH3B33Xbr888f+O01f7Puz9oX//yK/b39j229x3fse8x3vO4m3/P/9/1t634Ibd55xWc3L39h1e++e1e32fPAnf7vfv5m3/5zTf93rT94z4P3s3//pP6vX/zU2vtfqO/3u3Xl3b5n5br1j28l13fXg5tf5HneXff3O+/233zP2s3tX7zxz5v0U/4fbrtzf4+XN+y6+2m3f0fv04vI4c33vvx77X/mI7//sA/f5Aft3v+Ffe3ffcvz+v33mS/7mxf+/9t+6K+t29jbf+xrt27qG44d4i/1X4TfvuvbH2xfce3xI9N2P0q0l8g03/pX395z6i0331S84I1fvvn4a+vOfO0/fe31215+iHce2vL8vE+/5r4v/uL4s6599qUft9/1L9v7LnrbrZdf+rYrf+u0zS+u/f4/X3vdM+t39H3z+s1bv/P3H9jU8yvnrXzrG2664pLzX910yq4n7/+nP31f50ff/kO3XH/P//2+l243OxeftPL373vrxpefe+reW/pOfNufv/p/fv3Gq09a8f4vffb2p54+sA725S+c9+v3v+X+zde/e/3mbf1b1j19bseZX3nzmddcdv4F/c4f2Pn333xhy/O3f/q3n/iNDbftfOa+e27/53fd3PevO963s+/eD3zmF+evfv+1m34Wbvv0/1x49Rvu2j34l43P/Ew0sB3f990/ve3+E1/3nS/ddO43Pnn7227t//7f3f33m1Zfcv/tX3v3YzvW3XXHdz78vR3Xf+2+S25fe/363Vvuf3jr4/80MHT/x+/ffLz//c8fH+R/vv35i2s3PvG//9ePfXnrE/sObXrtO1/82qve8y/mrf6j/8e6G25615d/uOvj24a6T9vxx7d+s/j4v/7BqSvfddv7rvx0f2vv82t/evvvv+v53/zE2SvevGnrk5suftfnO1+85b3/3HHzL3S++Z1rFmxc19/73e++/s6mK/s3fXv33y1cecfHv/e+3y49vvbdq59Yd/tX7rtqwwuv3/S12y/s/XrfVbe889oLN//AHzj7rIduvvuB5//zR898t3mQ248yI/pE43d/P02mOfLwJm9wz95P/89v7rnur/+m669+c+kHvnvXFm9feMOf3/f4L17/+xfevvPqT92ycZpLp7e/sOGG537y63/z8f3X3/f/fP83m9b867fuWr+n87aPr3j3S2f2XfInX/v1Cza9cfvNl6966G9uX/3gD3q3/u3qT35+/f+3e8d/9x26sXfLzY++dM//3jZve/G8j86P+v4mN38zO/8f3vXU7y846x9+4drbrr72tS//k91vfu6qNfd/p++d6e6a0d3+f/PInXfsveS/feG2D43O/4trvv4fv56u5fE/f9m/fe93vvS39+69/b/Nf3v32xduvP013//m62+/c5vP/eC33v2/b1m31SfvI/f+4M/+vX/gmtuu/+jL13zx1m/s2fb/nnD2O2//5s/v/u1/63351i9/9+6n33Xf34QnvXv3r2++9m8/e1Xffbdv2fnfN/xGzy9+4o0/vef+0/qff4s99x41j9/0L/f56+e/5c63XfzWd2zc1j33t333v330p6978Yc3/OfX3/aKzfe/67pP/2fvt++8bM8Pf3fLffuOf+2f3nrf9a9578ef+X7o4p/400f/4t5/uv/2f534T+35a+vf/v019//Xv2q64s0/aP39/e3/33m463ev2/ytp3v+31tvu2731d/+ylp8uS738o1f+/Ztn/rC99b+R3/r5S+e98946f/1p/f9xf6P3Llh8f6bfvS12/vfcv6139/1gS/m7t+/12f5R96w+t4tX/7U53bsu2f3X2+5YdMv3v5/fe3aT7a8+/m3rtj1L2v2vf2G5/+6/1vf2XD32mff841/v6y741vfueX9N33z56t2r4aP/48pG+mI0YmX4E7cR/d890v/1S33vOb2d//xO//9x/9t9y1f3fyxL1/e3fH15d3fv/i3Pnv/y9uX3nr/79zzvTft+9qPdv/i2/7y4Lff3927dFvL6++54Uv/2nn6/3XWp++/5r86/61r598m5Xf03fW/S59/Yd/aT13/1mP2dHz6I5+92j/42e43//4N/2vtR5//51te3I4/sM9/aPPi9/z2q25qO+/GZ754S++2n3SdtvyNf3X9f33z3i03XnfX+s91fG5f5xtLnvja5q4v3fD4mve8952r33/1bdt+8f343v/9X7+35yv//k1fef7/4l//4x+3fH2s4/O3v3b18p/a097x+f93+ycf+7Uv/qD/D4e2v//b65/cceMft31s+aev+er9m96/9L+3vfvdr//+915/1vLqG/9l3de3f+zrv/q3y950xfL33P+f92/deP33f+d/rtvyxJ7bv/Xnrfcfv3T3q7++4Z6/Wfv1217+/O9se3f5m9//Xf/44vse2XzL4Xk5v1y4/aPvufzV513904cvvOiP/37v3e13ffrtd208q2XZlWf9z8/98J/ed9a2s992yxdvfMcf3PTm3u3/f/f69W87u9n4xM/+7O03PvGfXvK24U+tf33T51v8u3//tqf39226++b/tXj/4C98cv0n+l5f6l2wb8e2q5YseXz1k92Xf3TzNz/fdu7d598s636x5O9vvn3N4Xevvu/f96vP3fS+m/e1Pnr9/3/l2X+363u3vnT7/s9seG6ffuD1p330yv1bb/rnz//4zO/97O6/ee/qK/5w+y8u2fq16+69e83O3f2f/s5H153eueX419/5nTv3X3Xz29/eufm/Lrv3v919z+1vf92y5f/1m0+uvftf3vv5y/e+9PcfXP/tO29+z6q+O3+481O3/v673/T//d4133nnmSvuWP/1x/e3/OnqV/3+eT1vvv7fvvfBbf/x4GfWfG3L3I9ef9oV5y6/+P5PvfnL429f+/p3fvqJzW0X/eSsn4mXlPmnA1O6eJ/X5E9I32/2Xvv5/6i/839c894vvXf373XevX73zstOf2v/3O98df0n/mJ49+6PvG/12r+ve9e+V/9s1c7/uu817e4fPnLH9T/r8o5e/8j/+vM3vf343fXN23+x+uOnXpve+/n/cv9zX3/j/V/45K/3vP6y23e85e2/deN3vn3/1Zf94f997+f33fX4bbf94A1Xb/z2H932xft3PPXfT3/b4d6/aLrz+6svfvN9v//3b3jrq27d88rPvfX1a2/e8i/X/92G37zn5iuv33L3R1Y+/4X3f/p2+97O4qP3v+Nrf3P9xRfd/+7Pfu/ebzS71+3o/9wL7//74/Z9+v0fnLvy/B//53tv/I0br1v3iRve8o7V/3XnB2+7+/Nnv6XlS/3f+XTH8/vef+0pG3v/q3d49e6f/I+/P+3Vb/v2T980vOuK1eefee+G+y945f3//Z9mve5f+/a/+e3G9r/42y/d/4sfrn3d6cddduv4zV+m9/jOni/++4dPPXX1mR+d91/euf/L39i89Y6u3m+X/qOxe/2B4675H376aEunX/Xo7k5/40U9S/7m85/f8/Fbfve6q756zztf1fXf/u5vfuaq+b/c88C/vuvfPnX52a/v+O3f++e/6Ln7fT3Hq//mJ9/49A9+snX9Z5/+7Y+sWPWjS7783u+ve+4vvveprVd+9Z6ffs/f/2/9a1/14Xte/8W2z9+9Z8v/+I3jHv7Mv/zpZ9/7O7esWXXvE/e/64v3Pf/03e+44eOP3b355qUrv3vfT9+x4L8+seS2P3nLDTd/43OP3PTYqltvuO2/fGf7C//iX33mO6//3o3nPfv477/iyt3fece/f/K/7XjX/I+0vvf3V3/4y++//fM33XjX/Xf33Pqjtz580+33f+vA+Z+9o3+3s/7Wk43425f38q3v/S833/23N39x9ed/d/vjN6z89bO333rtvT96+L61d3//o8+1d/ztR14/vPXv19y+Ycct3161c+sn3/35l77/4a1f+cO43v/53b+665sX9f7f45778a+t/d0P/st/Wf/jP2p338kLhcyi2/z9/33i5T9q3fnE1/5292398939X/nhvU8uX335q49kU3L45CfeSObP54a4a8/q1S9937dvedNfP/qO97+/9X/duvbWW/33qfT3m4+/o6/lXevfe/V1f/j3l374i2vu33L4aA3/9jE9v//XW+6b3+r4gfe23fnMxttfeM/N73nly33lH9pW3/6eB54/3d1003V9C4fO/bE040p1qI+zXyYk3336U/ffcOPf/e1Pfn1u69o3Pve9x/ee8e5PvX/Dly7Y1Xb2S3e/7s2f/e5PPrs2f/iI2vL7v/SZT448f8Pvf+/W73y6t/m42q72m2+9/uMbfvh5T3LzTf/7jse8X/f6C884iYv48a0fWbr88itOW/Wv/e5+vU33f9U9qX/r/473vvY3vvKj1S98m4ff/qFvf63pD/pXX/T/1s4p1+S8f5SAnIrmz3x8Y3mYmGg4IBy4+c1bXvK7P7zhH9732fW/cv5pC444/S03/X3/419+94m/y+/jN36s4+uP/s0L37+tC/9jR65Lp2MceNIn/u+/O3fVqze43Svv/c0v8tbb3/09S5bM3S6+GvP+P79x6G8v6n38+49/fC9vv+vR2/e97jM/2fO5a9/50G23f/jFvN8qX051f+f/z0Imsx38jL939U3+Pbf851f//n89sf0dH2z9/Nfv+YevfufhVfS3L1q6p6f1/M0/6Xvfve/32x1/d8Xnv/7Mh/+m4Zq4H7mGv7rr8y996kX9b27b37f48bse2nL6jfev+uO/eOnP3X3p389df9W1/a5L1E22/2s48+wD81a629b3X/iFr/3jF1+v//02X249qZc6Xw7055OaZFYPj33x5g8u/Y01b+kZuvH/e+2Hk1v++xMv+733/87dF72t68xWf22mbfM+v2vN8P27D/S/Yt2L265uO93zZ214/19/dOXXf/S2nzt3SXP3+O016l1y810f+I2/fE3vxV943S0rt67f2feE7+m+oef5728aXfnh21b8y6d7yvS462++5s4lC/p29T55/x5m9c656dIjs6x++3M/e+jYqC6sP9/z7j+771NvXj1403/b/pEP3brmA43P/qfD0kU6e80b2r+95/D9d5d5/rG23s98yD/45/f0fv1Xb/vOvd//yX/uX738bL8f2m/a36Pevv2fWbn59S/67u0f/s8vf+m7W3+15cK2s2LceE9b/a3vv+L1t7z3vbe899brL3/j9Icf3L/i73/y+1/4qU13ff7820//pXvv+cItK/2/S4d23/eW1U8I03N10M9+mU3e7b/+2yvOf92a5/q7LnvoHbdse9O9N91+1d/3mPve+28P/eOlv1O5xS2XXb+5/3fved+/3fnhS96z6aWf3f+9V29at/6m+0998MefX1I43QG5049bNvd9/JbvXvm+L7zr/Wdf9+j3v/jLdz/0/k/f17H34euvW/fJNz12339d/l/9/f/43LdfduUnX7/2c7et/cCXb3f/4aX3/64/+u6f++x7n9/33Qee/vj6l3b/uG3f5s+uvf8zn1m76lP9i/v3+u63PveH193zN++5+13f/9K3vvGTr124eS8v/2fL+xO/8j/c9dOf99R15GjI1L3v/Q8p3f
"""

def render_saeis_logo(width=100):
    """دالة لعرض الشعار المدمج مباشرة بحجم متناسق"""
    clean_b64 = "".join(SAEIS_LOGO_B64.split())
    st.markdown(
        f'<div style="text-align: center;"><img src="data:image/png;base64,{clean_b64}" width="{width}px" style="border-radius:10px;"></div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 2. إدارة ذاكرة الجلسة (Session State Initialization)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "audit_data" not in st.session_state:
    # بيانات اختبار افتراضية تحاكي القيود المحاسبية
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": "JE-101", "Account": "Buildings & Equipment", "Debit": 15000.0, "Credit": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": "JE-102", "Account": "Inventory", "Debit": 8200.0, "Credit": 8200.0, "Standard": "IAS 2", "Status": "Passed", "Risk": "Low"},
        {"Entry_ID": "JE-103", "Account": "Receivables", "Debit": 3400.0, "Credit": 3000.0, "Standard": "IFRS 9", "Status": "Under Review", "Risk": "Medium"},
        {"Entry_ID": "JE-104", "Account": "Lease Liabilities", "Debit": 24000.0, "Credit": 24000.0, "Standard": "IFRS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": "JE-105", "Account": "Impairment Loss", "Debit": 5000.0, "Credit": 5000.0, "Standard": "IAS 36", "Status": "Passed", "Risk": "Low"}
    ])

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول الأسبوعية (Login Window)
# ---------------------------------------------------------
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_saeis_logo(width=140)
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>SAEIS Platform</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Smart Audit & Intelligence System</p>", unsafe_allow_html=True)
        st.divider()
        
        with st.form("login_form"):
            st.subheader("🔐 Login / تسجيل الدخول")
            user_input = st.text_input("Username / اسم المستخدم", value="Osama Abbas")
            pass_input = st.text_input("Password / كلمة السر", type="password")
            role_input = st.selectbox("Role / الصلاحية", ["Chief Auditor", "Senior Auditor", "External Auditor"])
            submit = st.form_submit_button("Sign In / دخول", type="primary", use_container_width=True)
            
            if submit:
                if pass_input == "123456": # كلمة السر الافتراضية
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_input
                    st.session_state.user_role = role_input
                    st.success("Access Granted! / تم تسجيل الدخول بنجاح")
                    st.rerun()
                else:
                    st.error("Invalid Credentials / كلمة السر غير صحيحة")
    st.stop()

# ---------------------------------------------------------
# 4. الشريط الجانبي والهيدر (Sidebar & Header)
# ---------------------------------------------------------
with st.sidebar:
    render_saeis_logo(width=110)
    st.session_state.lang = st.radio("🌐 Language / اللغة", ["EN", "AR"], horizontal=True)
    st.divider()
    
    st.markdown("### 👤 User Profile")
    st.write(f"**Name:** {st.session_state.get('user_name', 'Osama Abbas')}")
    st.write(f"**Role:** {st.session_state.get('user_role', 'Chief Auditor')}")
    st.divider()
    
    if st.button("🚪 Logout / خروج", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# القاموس واللغات
TXT = {
    "title": {"EN": "SAEIS - Smart Audit & Intelligence System", "AR": "SAEIS - نظام المراجعة والتدقيق الذكي"},
    "subtitle": {"EN": "Automated IFRS/IAS Compliance, Risk Analytics & ERP Integration Engine", "AR": "محرك أتمتة الامتثال لمعايير IFRS/IAS، تحليل المخاطر، والربط مع أنظمة ERP"},
    "tab1": {"EN": "📁 Data Ingestion", "AR": "📁 استيراد البيانات"},
    "tab2": {"EN": "📑 Live Editor & Audit", "AR": "📑 التعديل والمراجعة المباشرة"},
    "tab3": {"EN": "📊 Analytics & Risks", "AR": "📊 تحليلات المخاطر والامكانات"},
    "tab4": {"EN": "📚 IFRS Knowledge Base", "AR": "📚 مكتبة المعايير الدولية"}
}

L = st.session_state.lang

col_h1, col_h2 = st.columns([1, 6])
with col_h1:
    render_saeis_logo(width=85)
with col_h2:
    st.title(TXT["title"][L])
    st.caption(TXT["subtitle"][L])

st.divider()

# ---------------------------------------------------------
# 5. التبويبات التفاعلية والموديولات
# ---------------------------------------------------------
tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# --- Tab 1: Data Ingestion (استيراد البيانات) ---
with tabs[0]:
    st.subheader("Data Upload & ERP Integration" if L == "EN" else "استيراد ملفات القيود والربط السحابي")
    
    source = st.radio("Select Source:" if L == "EN" else "اختر مصدر البيانات:", ["Excel / CSV File", "ERP API Connection (Odoo / Onyx Pro)"], horizontal=True)
    
    if source == "Excel / CSV File":
        uploaded_file = st.file_uploader("Upload Trial Balance or Journal Entries" if L == "EN" else "اختر ملف القيود أو ميزان المراجعة:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_new = pd.read_csv(uploaded_file)
                else:
                    df_new = pd.read_excel(uploaded_file)
                st.session_state.audit_data = df_new
                st.success("File imported successfully!" if L == "EN" else "تم استيراد الملف وتحديث البيانات بنجاح!")
            except Exception as e:
                st.error(f"Error reading file: {e}" if L == "EN" else f"حدث خطأ أثناء قراءة الملف: {e}")
    else:
        st.info("🔗 API Live Integration Engine (Odoo v16+ & Onyx Pro ERP)")
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            st.text_input("ERP Endpoint URL", value="https://erp.company.com/api/v1/journal")
            st.text_input("API Key / Token", value="••••••••••••••••", type="password")
        with col_api2:
            st.selectbox("Target Fiscal Year", ["2026", "2025"])
            if st.button("Sync ERP Data Now" if L == "EN" else "مزامنة البيانات الآن", type="primary"):
                st.success("Data synced successfully from ERP!" if L == "EN" else "تمت المزامنة بنجاح من نظام ERP!")

# --- Tab 2: Live Editor & Audit (جدول المراجعة المباشر) ---
with tabs[1]:
    st.subheader("Interactive Audit Journal Table" if L == "EN" else "جدول القيود المحاسبية التفاعلي")
    
    df = st.session_state.audit_data
    
    # فحص التوازن التلقائي
    if "Debit" in df.columns and "Credit" in df.columns:
        total_debit = df["Debit"].sum()
        total_credit = df["Credit"].sum()
        diff = total_debit - total_credit
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Debit / إجمالي المدين", f"{total_debit:,.2f}")
        m2.metric("Total Credit / إجمالي الدائن", f"{total_credit:,.2f}")
        m3.metric("Imbalance / الفرق", f"{diff:,.2f}", delta_color="inverse" if diff != 0 else "normal")
        
        if diff != 0:
            st.warning("⚠️ Warning: Trial balance or Journal entries are out of balance!" if L == "EN" else "⚠️ تنبيه: إجمالي القيود غير متوازن!")
    
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 Save System Changes" if L == "EN" else "💾 حفظ التغييرات", type="primary"):
        st.session_state.audit_data = edited_df
        st.session_state.audit_logs.append(f"Data updated by {st.session_state.user_name}")
        st.success("Updated successfully! All changes are stored in session." if L == "EN" else "تم حفظ التغييرات بنجاح وتخزينها في الجلسة!")

# --- Tab 3: Analytics & Risk (تحليلات المخاطر والامتثال) ---
with tabs[2]:
    st.subheader("📊 Compliance & Audit Risk Dashboard" if L == "EN" else "📊 تحليلات الامتثال والمخاطر المحاسبية")
    
    df = st.session_state.audit_data
    if "Status" in df.columns and "Risk" in df.columns:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_status = px.pie(df, names="Status", title="Audit Status Distribution", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_status, use_container_width=True)
        with col_chart2:
            fig_risk = px.bar(df, x="Standard", y=df.columns[2] if len(df.columns) > 2 else "Entry_ID", color="Risk", title="Risk Exposure by IFRS Standard", barmode="group")
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("Upload dataset with Status and Risk columns to render analytics." if L == "EN" else "يرجى اختيار ملف يحتوي على تصنيفات المخاطر لعرض التحليلات.")

# --- Tab 4: Knowledge Base (المكتبة المعرفية) ---
with tabs[3]:
    st.subheader("📚 IFRS/IAS Knowledge Base & Rules" if L == "EN" else "📚 المكتبة المعرفية الشاملة لمعايير IFRS")
    
    selected_std = st.selectbox(
        "Select Standard / اختر المعيار:",
        [
            "IFRS 16 - Leases (عقود الإيجار)",
            "IAS 36 - Impairment of Assets (انخفاض قيمة الأصول)",
            "IAS 2 - Inventories (المخزون)",
            "IAS 1 - Presentation of Financial Statements (عرض القوائم المالية)"
        ]
    )
    st.divider()
    if "IFRS 16" in selected_std:
        st.markdown("### 🏢 IFRS 16: Leases")
        st.info("**Principle:** Eliminates off-balance sheet accounting for lessees by recognizing Right-of-Use (ROU) Assets and Lease Liabilities.")
        st.warning("**SAEIS Rule:** Detects rent expenses that must be capitalized on the balance sheet.")
    elif "IAS 36" in selected_std:
        st.markdown("### 📉 IAS 36: Impairment of Assets")
        st.info("**Principle:** Ensures that assets are carried at no more than their recoverable amount.")
        st.warning("**SAEIS Rule:** Triggers impairment review when asset carrying value exceeds recoverable limit.")