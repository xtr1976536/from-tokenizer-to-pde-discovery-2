# 去系数、展开函数的多变量 PDE 语料（200条）

每条记录给出原始来源、带参数形式、系数规范化后的可计算式。符号系数统一为单位系数，不能据此将新式解释为原论文的物理参数复现。
保留场的幂次和导数阶数。分母为零、对数定义域等数学限制仍适用。拉普拉斯在数值验证中按x/y展开。

## CF001 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=1+u^{2}\cdot v-u-u+\Delta(u)\\
\partial_{t}(v)=u-u^{2}\cdot v+\Delta(v)
\end{cases}
$$

来源：[ Spatiotemporal chaos and quasipatterns in coupled reaction-diffusion systems ](https://arxiv.org/src/2001.11730v2)

去除的系数：`A`, `B`, `D_u`, `D_v`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u} {\partial t} = A + u^2 v - Bu - u +D_u \nabla^2 u\\
\frac{\partial v} {\partial t} = Bu - u^2 v+D_v \nabla^2 v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF002 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)-u+v\\
\partial_{t}(v)=\partial_{xx}(v)-v
\end{cases}
$$

来源：[ Spatiotemporal pattern formation in nonlinear coupled reaction-diffusion systems with a mixed-type modal discontinuous Galerkin approach ](https://arxiv.org/src/2205.10755v1)

去除的系数：`\mu_{1}`, `\mu_{2}`, `k_{1}`, `k_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \mu_{1} \frac{\partial^{2} u}{\partial x^{2}} -k_{1}u +v\\
\frac{\partial v}{\partial t} = \mu_{2} \frac{\partial^{2} v}{\partial x^{2}} - k_{2}v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF003 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u^{2}\cdot v-u+1\\
\partial_{t}(v)=\partial_{xx}(v)-u^{2}\cdot v+u
\end{cases}
$$

来源：[ Spatiotemporal pattern formation in nonlinear coupled reaction-diffusion systems with a mixed-type modal discontinuous Galerkin approach ](https://arxiv.org/src/2205.10755v1)

去除的系数：`\mu_{1}`, `\mu_{2}`, `k_{1}`, `k_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \mu_{1} \frac{\partial^{2} u}{\partial x^{2}} + u^{2}v - (1+k_{2})u + k_{1}\\
\frac{\partial v}{\partial t} = \mu_{2} \frac{\partial^{2} v}{\partial x^{2}} - u^{2}v + k_{2} u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF004 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)-u\cdot v\\
\partial_{t}(v)=\partial_{xx}(v)+u\cdot v-v
\end{cases}
$$

来源：[ Spatiotemporal pattern formation in nonlinear coupled reaction-diffusion systems with a mixed-type modal discontinuous Galerkin approach ](https://arxiv.org/src/2205.10755v1)

去除的系数：`\mu_{1}`, `\mu_{2}`, `k_{1}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \mu_{1} \frac{\partial^{2} u}{\partial x^{2}} -uv\\
\frac{\partial v}{\partial t} = \mu_{2} \frac{\partial^{2} v}{\partial x^{2}} + uv -k_{1} v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF005 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u^{2}\cdot v-u+1\\
\partial_{t}(v)=\partial_{xx}(v)-u^{2}\cdot v+1
\end{cases}
$$

来源：[ Spatiotemporal pattern formation in nonlinear coupled reaction-diffusion systems with a mixed-type modal discontinuous Galerkin approach ](https://arxiv.org/src/2205.10755v1)

去除的系数：`\mu_{1}`, `\mu_{2}`, `k_{1}`, `k_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \mu_{1} \frac{\partial^{2} u}{\partial x^{2}} +u^{2}v - u + k_{1}\\
\frac{\partial v}{\partial t} = \mu_{2} \frac{\partial^{2} v}{\partial x^{2}} -u^{2}v + k_{2}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF006 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+\partial_{yy}(u)+u\cdot v^{2}-u+1\\
\partial_{t}(v)=\partial_{xx}(v)+\partial_{yy}(v)-u\cdot v^{2}+u
\end{cases}
$$

来源：[ Spatiotemporal pattern formation in nonlinear coupled reaction-diffusion systems with a mixed-type modal discontinuous Galerkin approach ](https://arxiv.org/src/2205.10755v1)

去除的系数：`\mu_{1}`, `\mu_{2}`, `k_{1}`, `k_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \mu_{1} [\frac{\partial^{2} u}{\partial x^{2}} + \frac{\partial^{2} u}{\partial y^{2}}] + uv^{2} - (1+k_{1}) u + k_{2}\\
\frac{\partial v}{\partial t} = \mu_{2} [\frac{\partial^{2} v}{\partial x^{2}} + \frac{\partial^{2} v}{\partial y^{2}}] - uv^{2} + k_{1} u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF007 · 4变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\frac{(w\cdot u^{2})}{v}-u+p+\Delta(u)\\
\partial_{t}(v)=w\cdot u^{2}-v+p+\Delta(v)\\
\partial_{t}(w)=1-w-p\cdot w+\Delta(w)\\
\partial_{t}(p)=u-p+\frac{(p^{2})}{1+p^{2}}+\Delta(p)
\end{cases}
$$

来源：[ Stationary peaks in a multivariable reaction--diffusion system: Foliated snaking due to subcritical Turing instability ](https://arxiv.org/src/2008.00094v4)

去除的系数：`D_{p}`, `D_{u}`, `D_{v}`, `D_{w}`, `\gamma`, `\mu`, `\nu`, `\rho_{u}`, `\rho_{v}`, `\varepsilon`, `c`, `c_0`, `d`, `e`, `f`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t}=c\dfrac{wu^2}{v}-\mu u+\rho_{u} p+D_{u} \nabla^2 u\\
\frac{\partial v}{\partial t}=cwu^2-\nu v+\rho_{v} p+D_{v} \nabla^2 v\\
\frac{\partial w}{\partial t}=c_0-\gamma w-\varepsilon p w+D_{w} \nabla^2 w\\
\frac{\partial p}{\partial t}=d u-ep+\dfrac{p^2}{1+fp^2}+D_{p} \nabla^2 p
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF008 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{x}(u\cdot v\cdot \partial_{x}(u))-\partial_{x}(u^{2}\cdot v\cdot \partial_{x}(v))+u\cdot v\\
\partial_{t}(v)=\partial_{xx}(v)-u\cdot v
\end{cases}
$$

来源：[ Uniqueness of Weak Solutions to One-Dimensional Doubly Degenerate Cross-Diffusion System ](https://arxiv.org/src/2501.06821v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = (uv u_x)_x - (u^2 v v_x)_x + uv\\
v_t = v_{xx} - uv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF009 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(1+u^{2}+u\cdot v)=u\cdot (1-u-v)\\
\partial_{t}(v)-\Delta(1+v^{2}+u\cdot v)=v\cdot (1-u-v)
\end{cases}
$$

来源：[ Stability of a cross-diffusion system and approximation by repulsive random walks: a duality approach ](https://arxiv.org/src/2109.07146v3)

去除的系数：`a_{11}`, `a_{12}`, `a_{21}`, `a_{22}`, `d_1u`, `d_2v`, `r_1`, `r_2`, `s_{11}`, `s_{12}`, `s_{21}`, `s_{22}`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_tu - \Delta( d_1u + a_{11} u^2+a_{12}uv ) = u(r_1-s_{11}u-s_{12}v)\\
\partial_tv - \Delta( d_2v + a_{22}v^2+a_{21}uv ) = v(r_2-s_{21}u-s_{22}v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF010 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(1+u\cdot v)=0\\
\partial_{t}(v)-\Delta(1+u\cdot v)=0
\end{cases}
$$

来源：[ Stability of a cross-diffusion system and approximation by repulsive random walks: a duality approach ](https://arxiv.org/src/2109.07146v3)

去除的系数：`a_{12}`, `a_{21}`, `d_1u`, `d_2v`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_tu - \Delta( d_1u + a_{12}uv ) = 0\\
\partial_tv - \Delta( d_2v + a_{21}uv ) = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF011 · 4变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=w\\
\partial_{t}(v)=p\\
\partial_{t}(w)=u-u^{3}+v-1-w+\partial_{xx}(u)+\partial_{xx}(v)\\
\partial_{t}(p)=1-u-v-p+\partial_{xx}(u)+\partial_{xx}(v)
\end{cases}
$$

来源：[ Designing reaction-cross-diffusion systems with Turing and wave instabilities ](https://arxiv.org/src/2409.06860v2)

去除的系数：`\tau`, `a`, `b`, `d_{11}`, `d_{12}`, `d_{21}`, `d_{22}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = w\\
\frac{\partial v}{\partial t} = p\\
\frac{\partial w}{\partial t} = \frac{1}{\tau} (u - a u^3 + v - b - w + d_{11} \frac{\partial^2 u}{\partial x^2} + d_{12} \frac{\partial^2 v}{\partial x^2})\\
\frac{\partial p}{\partial t} = \frac{1}{\tau} (b - u - 3 a v - p + d_{21} \frac{\partial^2 u}{\partial x^2} + d_{22} \frac{\partial^2 v}{\partial x^2})
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF012 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta((1+u+v)\cdot u)=u\cdot (1-u-1)\\
\partial_{t}(v)-\Delta((1+v)\cdot v)=v\cdot (1-v-u)
\end{cases}
$$

来源：[ Global smooth solutions for triangular reaction-cross diffusion systems ](https://arxiv.org/src/2202.10256v1)

去除的系数：`d_u`, `d_v`, `d_{\alpha}`, `d_{\beta}`, `d_{\gamma}`, `r_a`, `r_bv`, `r_c`, `r_d`, `r_u`, `r_v`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u - \Delta ( ( d_u+d_{\alpha} u + d_{\beta}v) u ) = u(r_u-r_a u-r_bv)\\
\partial_t v - \Delta ( (d_v +d_{\gamma}v) v ) = v(r_v-r_c v-r_d u)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF013 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta((1+u+v)\cdot u)=0\\
\partial_{t}(v)-\Delta((1+u+v)\cdot v)=0
\end{cases}
$$

来源：[ Perturbative global solutions of a large class of cross diffusion systems in any dimension ](https://arxiv.org/src/2403.00391v1)

去除的系数：`a_1`, `a_2`, `b_1`, `b_2`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u - \Delta[(d_1 + a_1 u +b_1 v)u] = 0\\
\partial_t v - \Delta[(d_2 + a_2 u+ b_2 v)v] = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF014 · 4变量 · haptotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+u\cdot (1-u)-u\cdot p\\
\partial_{t}(v)=(-(u+w))\cdot v\\
\partial_{t}(w)=\Delta(w)-\nabla\cdot(w\cdot \nabla(v))-w+u\cdot p\\
\partial_{t}(p)=\Delta(p)-p-u\cdot p+w
\end{cases}
$$

来源：[ Asymptotic behavior of a three-dimensional haptotactic cross-diffusion system modeling oncolytic virotherapy ](https://arxiv.org/src/2210.00484v1)

去除的系数：`D_p`, `\beta`, `\mu`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u-\nabla \cdot(u\nabla v)+\mu u(1-u)-up\\
v_t=-(u+w)v\\
w_t=\Delta w-\nabla \cdot(w\nabla v)-w+up\\
p_t=D_p\Delta p-p-up+\beta w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF015 · 4变量 · haptotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+u\cdot (1-u)-u\cdot p\\
\partial_{t}(v)=(-(u+w))\cdot v+v\cdot (1-v)\\
\partial_{t}(w)=\Delta(w)-\nabla\cdot(w\cdot \nabla(v))-w+u\cdot p\\
\partial_{t}(p)=\Delta(p)-p-u\cdot p+w
\end{cases}
$$

来源：[ Asymptotic behavior of a three-dimensional haptotactic cross-diffusion system modeling oncolytic virotherapy ](https://arxiv.org/src/2210.00484v1)

去除的系数：`D_p`, `D_u`, `D_w`, `\alpha_u`, `\alpha_w`, `\beta`, `\delta_p`, `\delta_w`, `\mu_u`, `\mu_v`, `\rho_p`, `\rho_u`, `\rho_w`, `\xi_u`, `\xi_w`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=D_u\Delta u-\xi_u\nabla\cdot(u\nabla v)+\mu_u u(1-u)-\rho_u up\\
v_t=- (\alpha_u u+\alpha_w w)v+\mu_v v(1-v)\\
w_t=D_w\Delta w-\xi_w\nabla\cdot(w\nabla v)- \delta_w w+\rho_w up\\
p_t=D_p\Delta p-\delta_p p-\rho_p up+\beta w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF016 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))\\
\partial_{t}(v)=\Delta(v)-u\cdot v
\end{cases}
$$

来源：[ Renormalized solutions to a chemotaxis system with consumption of chemoattractant ](https://arxiv.org/src/1803.05211v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u-\nabla\cdot(u\nabla v)\\
v_t=\Delta v-uv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF017 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+\nabla\cdot(u\cdot \nabla(w))\\
\partial_{t}(v)=\Delta(v)-v+u\\
\partial_{t}(w)=\Delta(w)-w+u
\end{cases}
$$

来源：[ Remarks on finite-time blow-up in a fully parabolic attraction-repulsion chemotaxis system via reduction to the Keller-Segel system ](https://arxiv.org/src/2103.02241v3)

去除的系数：`\alpha`, `\beta`, `\chi`, `\delta`, `\gamma`, `\xi`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u-\chi\nabla \cdot (u\nabla v)+\xi \nabla\cdot(u \nabla w)\\
v_t=\Delta v-\beta v+ \alpha u\\
w_t=\Delta w-\delta w+\gamma u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF018 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(\ln(v)))\\
\partial_{t}(v)=u\cdot v
\end{cases}
$$

来源：[ Global weak solutions and asymptotics of a singular PDE-ODE chemotaxis system with discontinuous data ](https://arxiv.org/src/1911.02157v1)

去除的系数：`\mu`, `\xi`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u- \nabla\cdot(\xi u \nabla\ln v)\\
v_t=- \mu u v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF019 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))\\
\partial_{t}(v)=\Delta(v)+u
\end{cases}
$$

来源：[ A sharp criterion and complete classification of global-in-time solutions and finite time blow-up of solutions to a chemotaxis system in supercritical dimensions ](https://arxiv.org/src/2601.15990v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \Delta u - \nabla \cdot (u\nabla v)\\
v_t = \Delta v + u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF020 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(w))\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(w))\\
\partial_{t}(w)=\Delta(w)-(u+v)\cdot w
\end{cases}
$$

来源：[ Boundedness and stabilization in a two-species chemotaxis system with signal absorption ](https://arxiv.org/src/1811.09343v1)

去除的系数：`\alpha`, `\beta`, `\chi_1`, `\chi_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u-\chi_1\nabla\cdot(u\nabla w)\\
v_t=\Delta v-\chi_2\nabla\cdot(v\nabla w)\\
w_t=\Delta w-(\alpha u+\beta v)w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF021 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(w))+1-u-1\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(w))+1-1-v\\
\partial_{t}(w)=\Delta(w)-(u+v)\cdot w
\end{cases}
$$

来源：[ Boundedness and stabilization in a two-species chemotaxis system with signal absorption ](https://arxiv.org/src/1811.09343v1)

去除的系数：`\alpha`, `\beta`, `\chi_1`, `\chi_2`, `\mu_1u`, `\mu_2v`, `a_1v`, `a_2u`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u-\chi_1\nabla\cdot(u\nabla w)+\mu_1u(1-u-a_1v)\\
v_t=\Delta v-\chi_2\nabla\cdot(v\nabla w)+\mu_2v(1-a_2u-v)\\
w_t=\Delta w-(\alpha u+\beta v)w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF022 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)-\partial_{x}(u\cdot v)=\partial_{xx}(u)\\
\partial_{t}(v)-\partial_{x}(u)=0
\end{cases}
$$

来源：[ Convergence to traveling waves of a singular PDE-ODE hybrid chemotaxis system in the half space ](https://arxiv.org/src/1909.03171v1)

去除的系数：`D`, `\chi`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-\chi(uv)_x=Du_{xx}\\
v_t-u_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF023 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))\\
\partial_{t}(v)=\Delta(v)-v+u
\end{cases}
$$

来源：[ Boundedness and finite-time blow-up in a quasilinear parabolic-elliptic chemotaxis system with logistic source and nonlinear production ](https://arxiv.org/src/2105.08942v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u - \nabla \cdot (u\nabla v)\\
v_t=\Delta v - v + u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF024 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+u\cdot (1-u)\\
\partial_{t}(v)=\Delta(v)-v+u
\end{cases}
$$

来源：[ Persistence and convergence in parabolic-parabolic chemotaxis system with logistic source on $\mathbb{R}^{N}$ ](https://arxiv.org/src/2103.04265v2)

去除的系数：`\chi`, `\lambda`, `\mu`, `a`, `b`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=\Delta u - \chi\nabla\cdot ( u\nabla v) + u(a-bu)\\
{v_t}=\Delta v -\lambda v+\mu u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF025 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+u\cdot (1-u)\\
\partial_{t}(v)=\Delta(v)-u\cdot v
\end{cases}
$$

来源：[ The spreading of global solutions of chemotaxis systems with logistic source and consumption on $\mathbb{R}^{N}$ ](https://arxiv.org/src/2405.19428v2)

去除的系数：`\chi`, `\tau`, `a`, `b`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_tu=\Delta u - \chi\nabla\cdot(u\nabla v)+ u(a-bu)\\
{\tau \partial_tv}=\Delta v-uv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF026 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\partial_{rr}(u)+\frac{(1)}{r}\cdot \partial_{r}(u)+\partial_{r}(u)\cdot \partial_{r}(v)+u\cdot \partial_{rr}(v)+\frac{(1)}{r}\cdot u\cdot \partial_{r}(v)\\
\partial_{t}(v)=(-v)\cdot u
\end{cases}
$$

来源：[ An Efficient Particle-Field Algorithm with Neural Interpolation based on a Parabolic-Hyperbolic Chemotaxis System in 3D ](https://arxiv.org/src/2510.13199v3)

去除的系数：`\chi`, `\gamma`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \gamma (u_{rr} + \frac{2}{r}u_r) + \chi (u_rv_r + u v_{rr} + \frac{2}{r}u v_r)\\
v_t = -v u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF027 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))\\
\partial_{t}(v)=\Delta(v)-v+w\\
\partial_{t}(w)=\Delta(w)-w+u
\end{cases}
$$

来源：[ Parabolic-elliptic and indirect-direct simplifications in chemotaxis systems driven by indirect signalling ](https://arxiv.org/src/2508.01436v2)

去除的系数：`\tau`, `\varepsilon`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = \Delta u - \nabla \cdot (u \nabla v )\\
\varepsilon \partial_t v = \Delta v - v + w\\
\varepsilon \partial_t w = \tau \Delta w - w + u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF028 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+\partial_{x}(u)-\partial_{x}(u\cdot \partial_{x}(v))+u\cdot (1-u)\\
\partial_{t}(v)=\partial_{xx}(v)+\partial_{x}(v)-v+u
\end{cases}
$$

来源：[ Existence of Traveling wave solutions of parabolic-parabolic chemotaxis systems ](https://arxiv.org/src/1610.05215v2)

去除的系数：`\chi`, `\tau`, `a`, `b`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=u_{xx}+cu_x -\chi (u v_x)_x + u(a-bu)\\
\tau v_t=v_{xx}+\tau c v_x-v+u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF029 · 2变量 · magnetohydrodynamics

$$
\begin{cases}
\partial_{t}(u)+\partial_{y}(u)\cdot \partial_{x}(v)-\partial_{x}(u)\cdot \partial_{y}(v)=\Delta(u)\\
\partial_{t}(v)-\partial_{y}(u)\cdot \Delta(\partial_{x}(u))+\partial_{x}(u)\cdot \Delta(\partial_{y}(u))=\Delta(v)
\end{cases}
$$

来源：[ A Gradient Recovery Method for Electron Magnetohydrodynamics with Fractional Dissipation ](https://arxiv.org/src/2606.19716v1)

去除的系数：`\mu`, `\nu`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u + u_y v_x - u_x v_y = \mu\Delta u\\
\partial_t v - u_y\Delta u_x + u_x\Delta u_y = \nu\Delta v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF030 · 2变量 · wave

$$
\begin{cases}
\partial_{tt}(u)-\Delta(u)+\partial_{t}(v)=0\\
\partial_{tt}(v)-\Delta(v)-\partial_{t}(u)=0
\end{cases}
$$

来源：[ Indirect stability of a multidimensional coupled wave equations with one locally boundary fractional damping ](https://arxiv.org/src/2104.03389v1)

去除的系数：`a`, `b`

<details><summary>对应原式与处理记录</summary>

```latex
u_{tt}-\Delta u+bv_t=0\\
v_{tt}-a\Delta v-bu_t=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF031 · 2变量 · wave

$$
\begin{cases}
\partial_{tt}(u)-\partial_{xx}(u)+\partial_{t}(v)=0\\
\partial_{tt}(v)-\partial_{xx}(v)-\partial_{t}(u)=0
\end{cases}
$$

来源：[ Indirect stability of a multidimensional coupled wave equations with one locally boundary fractional damping ](https://arxiv.org/src/2104.03389v1)

去除的系数：`a`, `b`

<details><summary>对应原式与处理记录</summary>

```latex
u_{tt}-u_{xx}+bv_t=0\\
v_{tt}-av_{xx}-bu_t=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF032 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)-v\cdot \partial_{x}(v)+\partial_{xxx}(u)=0\\
\partial_{t}(v)+u\cdot \partial_{x}(v)+v\cdot \partial_{x}(u)+\partial_{xxx}(v)=0
\end{cases}
$$

来源：[ New Complexiton Solutions of the KdV and Coupled KdV Equations ](https://arxiv.org/src/1605.05233v1)

去除的系数：`\rho`, `\zeta`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+\zeta uu_x-\zeta vv_x+\rho u_{xxx}=0\\
v_t+\zeta uv_x+\zeta vu_x+\rho v_{xxx}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF033 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)-\partial_{xxx}(u)+u\cdot \partial_{x}(u)=\partial_{xxx}(v)+\partial_{x}(u\cdot v)\\
\partial_{t}(v)-\partial_{xxx}(v)+v\cdot \partial_{x}(v)=\partial_{xxx}(u)+\partial_{x}(u\cdot v)
\end{cases}
$$

来源：[ Multiple-scale analysis on the radiation within the coupled KdV equations ](https://arxiv.org/src/1609.09574v1)

去除的系数：`\gamma`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-(1-\gamma)u_{xxx}+uu_x=\gamma v_{xxx}+\frac{(uv)_x}{2}\\
v_t-(1-\gamma)v_{xxx}+vv_x=\gamma u_{xxx}+\frac{(uv)_x}{2}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF034 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)-\partial_{xxx}(u)+u\cdot \partial_{x}(u)=\partial_{x}(u\cdot v)\\
\partial_{t}(v)-\partial_{xxx}(v)+v\cdot \partial_{x}(v)=\partial_{x}(u\cdot v)
\end{cases}
$$

来源：[ Multiple-scale analysis on the radiation within the coupled KdV equations ](https://arxiv.org/src/1609.09574v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t-u_{xxx}+uu_x=\frac{(uv)_x}{2}\\
v_t-v_{xxx}+vv_x=\frac{(uv)_x}{2}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF035 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v\cdot u)+\partial_{xxx}(v)=0\\
\partial_{t}(v)+v\cdot \partial_{x}(v)+\partial_{x}(u)=0
\end{cases}
$$

来源：[ Traveling Wave Solutions of Degenerate Coupled KdV Equation ](https://arxiv.org/src/1308.5649v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}+(vu)_{x}+\frac{1}{4}v_{xxx}=0\\
v_{t}+vv_{x}+u_{x}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF036 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=u\cdot \partial_{x}(u)+u\cdot \partial_{x}(u)+\partial_{x}(v)\\
\partial_{t}(v)=\partial_{xxx}(u)+v\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ Traveling Wave Solutions of Degenerate Coupled KdV Equation ](https://arxiv.org/src/1308.5649v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=uu_x+\frac{1}{2}uu_x+v_x\\
v_t=-\frac{1}{4}u_{xxx}+v u_x+\frac{1}{2}uv_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF037 · 3变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=u\cdot \partial_{x}(u)+u\cdot \partial_{x}(u)+\partial_{x}(v)\\
\partial_{t}(v)=v\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)+\partial_{x}(w)\\
\partial_{t}(w)=\partial_{xxx}(u)+w\cdot \partial_{x}(u)+u\cdot \partial_{x}(w)
\end{cases}
$$

来源：[ Traveling Wave Solutions of Degenerate Coupled KdV Equation ](https://arxiv.org/src/1308.5649v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=uu_x+\frac{1}{2}uu_x+v_x\\
v_t=v u_x+\frac{1}{2}uv_x+w_x\\
w_t=-\frac{1}{4}u_{xxx}+w u_x+\frac{1}{2}uw_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF038 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=u^{3}\cdot \partial_{xxx}(u)+u^{3}\cdot \partial_{x}(u)\cdot \partial_{xx}(v)+u^{4}\cdot \partial_{x}(v)\cdot \partial_{xx}(v)\\
\partial_{t}(v)=u^{3}\cdot \partial_{xxx}(v)-u^{2}\cdot \partial_{x}(u)\cdot \partial_{xx}(v)-u^{2}\cdot \partial_{xx}(u)\cdot \partial_{x}(v)-u^{3}\cdot \partial_{xxx}(v)
\end{cases}
$$

来源：[ Transformation of a generalized Harry Dym equation into the Hirota--Satsuma system ](https://arxiv.org/src/nlin/0309077v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = u^3 u_{xxx} + 12 u^3 u_x v_x^2 + 12 u^4 v_x v_{xx}\\
v_t = - 2 u^3 v_{xxx} - 6 u^2 u_x v_{xx} - 6 u^2 u_{xx} v_x - 8 u^3 v_x^3
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF039 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{yyy}(u)-\frac{((\partial_{yy}(u))^{2})}{\partial_{y}(u)}+\partial_{y}(u)\cdot \partial_{yy}(v)\\
\partial_{t}(v)=\partial_{yyy}(v)-\partial_{yyy}(v)-(\frac{(\partial_{yyy}(u))}{\partial_{y}(u)}-\frac{((\partial_{yy}(u))^{2})}{\partial_{yy}(u)})\cdot \partial_{y}(v)
\end{cases}
$$

来源：[ Transformation of a generalized Harry Dym equation into the Hirota--Satsuma system ](https://arxiv.org/src/nlin/0309077v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = u_{yyy} - \frac{3 u_{yy}^2}{2 u_y} + 6 u_y v_y^2\\
v_t = - 2 v_{yyy} - 2 v_y^3 - 3 ( \frac{u_{yyy}}{u_y} - \frac{3 u_{yy}^2}{2 u_y^2} ) v_y
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF040 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{y}(\partial_{yy}(u)+v\cdot \partial_{y}(v)-u^{3}+u\cdot v^{2})\\
\partial_{t}(v)=\partial_{y}(\partial_{yy}(v)-v\cdot \partial_{y}(u)+u^{2}\cdot v-v^{3})
\end{cases}
$$

来源：[ Transformation of a generalized Harry Dym equation into the Hirota--Satsuma system ](https://arxiv.org/src/nlin/0309077v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = ( u_{yy} + 12 v v_y - \tfrac{1}{2} u^3 + 6 u v^2 )_y\\
v_t = ( - 2 v_{yy} - 3 v u_y + \tfrac{3}{2} u^2 v - 2 v^3 )_y
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF041 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+\partial_{xxx}(v)+v\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)\\
\partial_{t}(v)=\partial_{xxx}(v)-u\cdot \partial_{x}(u)+v\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)+v\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ The Integrability of New Two-Component KdV Equation ](https://arxiv.org/src/0910.2389v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = u_{xxx} + v_{xxx} + 2vu_{x} + 2uv_x\\
v_t = v_{xxx} - 9u u_x + 6 vu_x + 3uv_x + 2vv_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF042 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+\partial_{xxx}(v)+u\cdot \partial_{x}(u)+v\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)\\
\partial_{t}(v)=\partial_{xxx}(u)+\partial_{xxx}(v)-v\cdot \partial_{x}(u)-u\cdot \partial_{x}(v)-v\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ The Integrability of New Two-Component KdV Equation ](https://arxiv.org/src/0910.2389v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = 4u_{xxx} +3v_{xxx} + 4uu_x + vu_x + 2uv_x\\
v_t = 3u_{xxx} + v_{xxx} -4vu_x - 2uv_x - 2vv_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF043 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=u^{2}\cdot \partial_{x}(\partial_{xx}(u)\cdot u+\partial_{xx}(v)\cdot u^{2}+\partial_{x}(\partial_{x}(v)\cdot u^{2}))\\
\partial_{t}(v)=\partial_{xxx}(u)-\partial_{xxx}(v)\cdot u^{3}-\partial_{x}(v)\cdot u^{2}\cdot (\partial_{x}(v)\cdot \partial_{x}(u)+\partial_{xx}(u))-\partial_{x}(\partial_{xx}(u)\cdot u+\partial_{xx}(v)\cdot u^{3}+\partial_{x}(v)\cdot \partial_{x}(u)\cdot u^{2})
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{u^2}{2} (4u_{xx}u + v_x^2 u^2 + 2(v_xu^2)_x )_x\\
v_t = \frac{1}{2} (2u_x^3 - v_x^3u^3 - 2v_xu^2(v_xu_x + u_{xx}) - (2u_x^2u+v_x^2u^3+2v_xu_xu^2)_x )
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF044 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{y}(\partial_{yy}(u)+u^{3}+\partial_{yy}(v)+\partial_{y}(v)\cdot u-v\cdot \partial_{y}(v)-v^{2}\cdot u)\\
\partial_{t}(v)=\partial_{y}(\partial_{yy}(u)-\partial_{y}(u)\cdot u+\partial_{yy}(v)+v^{3}+v\cdot \partial_{y}(u)-v\cdot u^{2})
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{1}{20} (-2u_{yy} + u^3 + 18v_{yy} + 18v_yu-162v v_y - 81v^2u )_y\\
v_t = \frac{1}{20} ( 2u_{yy} - 2u_yu + 22v_{yy} + 9v^3 + 18vu_y - 9vu^2 )_y
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF045 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{y}(\partial_{yy}(u)-u^{3}-v^{2}-\partial_{y}(v)\cdot u+\partial_{y}(v)\cdot v+v^{2}\cdot u)\\
\partial_{t}(v)=\partial_{y}(\partial_{yy}(u)+\partial_{y}(u)\cdot u+\partial_{yy}(v)-v^{3}-v\cdot \partial_{y}(u)+v\cdot u^{2})
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t =\frac{1}{8}(2u_{yy} - u^3 - 18v^2 - 18v_yu + 54v_yv + 27v^2u)_y\\
v_t = \frac{1}{8}(-2u_{yy} + u_yu + 2v_{yy} - 9v^3 - 6vu_y + 3vu^2)_y
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF046 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{y}(\partial_{y}(\partial_{y}(u)+\partial_{y}(v)+u^{2}+v^{2}+v\cdot u)+\partial_{y}(v)\cdot u+v^{2}\cdot u+v\cdot u^{2})\\
\partial_{t}(v)=\partial_{y}(\partial_{y}(u^{2}+v^{2}+v\cdot \partial_{y}(u))+v^{3}+v^{2}\cdot u+v\cdot u^{2})
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{1}{4} ( ( 4u_{y} + 2v_{y} +2u^2 + v^2 + 2vu)_y + 2v_yu + v^2u + 2vu^2 )_y\\
v_t = - \frac{1}{4} ( (4u^2 + v^2 + 4vu_y)_y + v^3 + 4v^2u + 4vu^2 )_y
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF047 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{yyy}(u)+\partial_{yyy}(v)+u\cdot \partial_{y}(u)-u\cdot \partial_{y}(v)-v\cdot \partial_{y}(v)-v\cdot \partial_{y}(u)\\
\partial_{t}(v)=\partial_{yyy}(u)+\partial_{yyy}(v)-u\cdot \partial_{y}(u)-u\cdot \partial_{y}(v)+v\cdot \partial_{y}(v)-v\cdot \partial_{y}(u)
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{1}{20} (- 2u_{yyy} + 18v_{yyy} + 9uu_y - 9u v_y - 405v v_y-27v u_y)\\
v_t = \frac{1}{20} (2u_{yyy} + 22v_{yyy} -5u u_y -27u v_y + 9v v_y - 9v u_y)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF048 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{yyy}(u)+u\cdot \partial_{y}(u)-\partial_{yyy}(v)-u\cdot \partial_{y}(v)-v\cdot \partial_{y}(u)\\
\partial_{t}(v)=-\partial_{yyy}(u)+\partial_{yyy}(v)-u\cdot \partial_{y}(v)-v\cdot \partial_{y}(u)+v\cdot \partial_{y}(v)
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{1}{4}(u_{yyy} +3u u_y - 9v_{yyy} - 18u v_y - 9v u_y)\\
v_t = \frac{1}{4}(-u_{yyy}+ v_{yyy} - 3uv_y -6v u_y + 9vv_y )
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF049 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{y}(\partial_{x}(\partial_{yy}(u)+\partial_{yy}(v)+u^{2}+u\cdot v)+\partial_{x}(v)\cdot u)\\
\partial_{t}(v)=\partial_{y}(u^{2}+v\cdot u+v^{2})
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{1}{2} ( ( 2u_{yy} +v_{yy} +3u^2 + uv )_x +v_xu )_y\\
v_t =-\frac{3}{4} (4u^2 + 2vu + v^2)_y
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF050 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)-\partial_{x}(v)\cdot u-v\cdot \partial_{x}(u)\\
\partial_{t}(v)=\partial_{y}(u)\cdot u
\end{cases}
$$

来源：[ Two-Component Coupled KdV Equations and its Connection with the Generalized Harry Dym Equation ](https://arxiv.org/src/1210.5822v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \frac{1}{2} (2u_{xxx} - v_x u - 2v u_x )\\
v_t =-6u_yu
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF051 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)-\partial_{x}(u\cdot v)\\
\partial_{t}(v)=\partial_{xxx}(v)-u\cdot \partial_{x}(u)
\end{cases}
$$

来源：[ Global Well-posedness of a System of Nonlinearly Coupled KdV equations of Majda and Biello ](https://arxiv.org/src/1310.1130v1)

去除的系数：`\alpha`

<details><summary>对应原式与处理记录</summary>

```latex
u_t =\alpha u_{xxx} - (uv)_x\\
v_t = v_{xxx} - u u_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF052 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxx}(u)+\partial_{x}(v\cdot v)=0\\
\partial_{t}(v)+\partial_{xxx}(v)+\partial_{x}(u\cdot v)=0
\end{cases}
$$

来源：[ Nonsqueezing property of the coupled KdV type system without Miura transform ](https://arxiv.org/src/1509.08114v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t + u_{xxx} + \frac{1}{2}(vv)_x = 0\\
v_t + v_{xxx} + (uv)_x =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF053 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=u\cdot \partial_{x}(u)-v\cdot \partial_{x}(v)-\partial_{x}(v)-\partial_{xxx}(v)\\
\partial_{t}(v)=-\partial_{x}(u)-\partial_{x}(u\cdot v)-\partial_{xxx}(u)
\end{cases}
$$

来源：[ Structure-preserving reduced-order modelling of Korteweg de Vries equation ](https://arxiv.org/src/2004.08509v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = \frac{3}{2} u\partial_x u - \frac{1}{2} v\partial_xv -\partial_x v -\frac{1}{6}\partial_{xxx}v\\
\partial_t v = -\partial_x u - \frac{1}{2}\partial_x (uv) - \frac{1}{6}\partial_{xxx}u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF054 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+v\cdot \partial_{x}(v)+u\cdot \partial_{x}(u)+\partial_{xxx}(u)=0\\
\partial_{t}(v)+v\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)+\partial_{xxx}(v)=0
\end{cases}
$$

来源：[ Multi-soliton, multi-positon, multi-negaton, and multi-periodic solutions of the coupled Volterra lattice equation ](https://arxiv.org/src/0911.3458v1)

去除的系数：`\alpha`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+6\alpha vv_x+6uu_x+u_{xxx}=0\\
v_t+6vu_x+6uv_x+v_{xxx}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF055 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)-\partial_{xxt}(u)=u\cdot \partial_{xxx}(u)+\partial_{x}(u)\cdot \partial_{xx}(u)-u\cdot \partial_{x}(u)+v\cdot \partial_{xx}(v)+\partial_{x}(v)\cdot \partial_{xxx}(v)\\
\partial_{xxt}(v)-\partial_{t}(v)=u\cdot \partial_{x}(v)+\partial_{x}(u)\cdot v-u\cdot \partial_{xxx}(v)-\partial_{xx}(u)\cdot \partial_{x}(v)-\partial_{x}(u)\cdot \partial_{xx}(v)
\end{cases}
$$

来源：[ Euler Equations Related to the Generalized Neveu-Schwarz Algebra ](https://arxiv.org/src/1306.3628v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t-u_{xxt}=uu_{xxx}+2u_xu_{xx}-3uu_x+\frac{3}{8}vv_{xx}+\frac{1}{2}v_xv_{xxx}\\
v_{xxt}-\frac{1}{4}v_t=\frac{3}{4}uv_x+\frac{3}{8}u_xv-uv_{xxx}-\frac{1}{2}u_{xx} v_x-\frac{3}{2}u_xv_{xx}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF056 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)-u\cdot \partial_{x}(u)+\partial_{x}(v)+\partial_{x}(u)\\
\partial_{t}(v)=(-\partial_{x}(u))\cdot v-u\cdot \partial_{x}(v)+\partial_{x}(v)
\end{cases}
$$

来源：[ Direct integral method, complete discrimination system for polynomial and applications to classifications of all single traveling wave solutions to nonlinear differential equations:a survey ](https://arxiv.org/src/nlin/0609058v1)

去除的系数：`\varepsilon`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\frac{1}{4}u_{xxx}-\frac{3}{2}uu_x+v_x+\varepsilon u_x\\
v_t=-u_xv-\frac{1}{2}uv_x+\varepsilon v_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF057 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(1)+\partial_{x}(u)+\partial_{xxx}(1)=0\\
\partial_{t}(v)+\partial_{x}(u\cdot v)+\partial_{x}(1)=0
\end{cases}
$$

来源：[ Direct integral method, complete discrimination system for polynomial and applications to classifications of all single traveling wave solutions to nonlinear differential equations:a survey ](https://arxiv.org/src/nlin/0609058v1)

去除的系数：`\eta_1`, `\eta_2vv`, `\varepsilon_1v`, `\varepsilon_2u`, `\varepsilon_3u`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+\varepsilon_1v_x+\varepsilon_2u^2u_x+\varepsilon_3u_{xxx}=0\\
v_t+\eta_1(uv)_x+\eta_2vv_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF058 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(1)+\partial_{x}(1)+\partial_{xxx}(1)=0\\
\partial_{t}(v)+\partial_{x}(u\cdot v)+\partial_{x}(1)=0
\end{cases}
$$

来源：[ Direct integral method, complete discrimination system for polynomial and applications to classifications of all single traveling wave solutions to nonlinear differential equations:a survey ](https://arxiv.org/src/nlin/0609058v1)

去除的系数：`\eta_1`, `\eta_2vv`, `\varepsilon_1vv`, `\varepsilon_2uu`, `\varepsilon_3u`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+\varepsilon_1vv_x+\varepsilon_2uu_x+\varepsilon_3u_{xxx}=0\\
v_t+\eta_1(uv)_x+\eta_2vv_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF059 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ The Linearized Classical Boussinesq System on the Half-Line ](https://arxiv.org/src/2009.09532v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x + (uv)_x = 0\\
v_t + u_x + vv_x - v_{xxt} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF060 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)+\partial_{xxx}(v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(v^{2})+\partial_{xxx}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Local discontinuous Galerkin methods for the abcd nonlinear Boussinesq system ](https://arxiv.org/src/2110.04339v1)

去除的系数：`a`, `b`, `c`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+(u v)_x+av_{xxx}-bu_{xxt}=0\\
v_t+u_x+(\frac{v^2}{2})_x+cu_{xxx}-dv_{xxt}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF061 · 2变量 · forced_boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)+\partial_{xxx}(v)-\partial_{xxt}(u)=\cos(x+t)+\cos(x+t)-\sin(x+t)\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(v^{2})+\partial_{xxx}(u)-\partial_{xxt}(v)=\sin(x+t)+\cos(x+t)-\sin(x+t)
\end{cases}
$$

来源：[ Local discontinuous Galerkin methods for the abcd nonlinear Boussinesq system ](https://arxiv.org/src/2110.04339v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+(u v)_x+\frac{1}{12}v_{xxx}-\frac{1}{18}u_{xxt}=\cos(2x+2t)+\frac{11}{12}\cos(x+t)-\frac{19}{18}\sin(x+t)\\
v_t+u_x+(\frac{v^2}{2})_x+\frac{1}{12}u_{xxx}-\frac{1}{9}v_{xxt}=\frac{1}{2}\sin(2x+2t)+\frac{10}{9}\cos(x+t)-\frac{11}{12}\sin(x+t)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF062 · 2变量 · forced_boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)+\partial_{xxx}(v)-\partial_{xxt}(u)=\cos(x+t)+\cos(x+t)-\sin(x+t)\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(v^{2})+\partial_{xxx}(u)=\cos(x+t)+\cos(x+t)-\sin(x+t)
\end{cases}
$$

来源：[ Local discontinuous Galerkin methods for the abcd nonlinear Boussinesq system ](https://arxiv.org/src/2110.04339v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+(u v)_x+\frac{1}{9}v_{xxx}-\frac{1}{9}u_{xxt}=\cos(2x+2t)+\frac{8}{9}\cos(x+t)-\frac{10}{9}\sin(x+t)\\
v_t+u_x+(\frac{v^2}{2})_x+\frac{1}{9}u_{xxx}=\frac{1}{2}\cos(2x+2t)+\cos(x+t)-\frac{8}{9}\sin(x+t)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF063 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+u\cdot \partial_{x}(u)+\partial_{xtt}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(u\cdot v)=0
\end{cases}
$$

来源：[ Dissipative Boussinesq System of Equations in the Bénard-Marangoni Phenomenon ](https://arxiv.org/src/patt-sol/9306002v1)

去除的系数：`\Lambda`, `\delta`, `\epsilon`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + c^2 v_x + \epsilon u u_x + \delta^2 \Lambda v_{xtt} = 0\\
v_t + u_x + \epsilon (u v)_x = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF064 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+u\cdot \partial_{x}(u)-\partial_{xx}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(u)\cdot v+u\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ Dissipative Boussinesq System of Equations in the Bénard-Marangoni Phenomenon ](https://arxiv.org/src/patt-sol/9306002v1)

去除的系数：`\alpha`, `c`, `c_0`, `d`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + c^2 g v_x + uu_x - \alpha d c_0 u_{xx} = 0\\
v_t + d u_x + u_x v + uv_x = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF065 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+u\cdot \partial_{x}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)\cdot v+u\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ Dissipative Boussinesq System of Equations in the Bénard-Marangoni Phenomenon ](https://arxiv.org/src/patt-sol/9306002v1)

去除的系数：`c`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + c^2 g v_x + u u_x = 0\\
v_t + u_x v + u v_x = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF066 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)-\partial_{xx}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)=0
\end{cases}
$$

来源：[ Dissipative Boussinesq System of Equations in the Bénard-Marangoni Phenomenon ](https://arxiv.org/src/patt-sol/9306002v1)

去除的系数：`\alpha`, `c`, `c_0`, `d`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + c^2 g v_x - \alpha d c_0 u_{xx} = 0\\
v_t + d u_x = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF067 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(u\cdot u)+\partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(u\cdot v)+\partial_{x}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Stationary Expansion Shocks for a Regularized Boussinesq System ](https://arxiv.org/src/1612.04750v1)

去除的系数：`h`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + (uu)_x + (h v)_x = 0\\
v_t + (uv)_x + u_x - \frac{1}{3} v_{xxt} =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF068 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(v\cdot u)+\partial_{xxx}(v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)+\partial_{xxx}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ The classical Boussinesq system revisited ](https://arxiv.org/src/2001.11870v1)

去除的系数：`a`, `b`, `c`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+(vu)_x + av_{xxx}-bu_{xxt}=0\\
v_t+u_x+vv_x+cu_{xxx}-dv_{xxt}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF069 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)=0\\
\partial_{t}(v)+u\cdot \partial_{x}(v)=\partial_{x}(u)
\end{cases}
$$

来源：[ Finite time blow up for a 1D model of 2D Boussinesq system ](https://arxiv.org/src/1312.4913v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u(t,x) + u(t,x)\partial_xu(t,x)=0\\
\partial_t v(t,x)+u(t,x)\partial_x v(t,x)=\partial_xu(t,x)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF070 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)-\partial_{xxt}(v)=\partial_{xx}(v)
\end{cases}
$$

来源：[ Long-Time Asymptotic Behavior of Dissipative Boussinesq System ](https://arxiv.org/src/math/0607708v1)

去除的系数：`b`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x-b u_{xxt}=0\\
v_t+u_x-d v_{xxt}=v_{xx}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF071 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{xxx}(v)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{xxx}(u)+v\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ Asymptotic behavior of Boussinesq system of KdV-KdV type ](https://arxiv.org/src/1709.06192v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x+v_{xxx}+ (u v)_x= 0\\
v_t +u_x +u_{xxx} +vv_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF072 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(v\cdot u)+\partial_{xxx}(v)-\partial_{xxt}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)+\partial_{xxx}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Hexagonal standing wave patterns of a two-dimensional Boussinesq system ](https://arxiv.org/src/1811.05952v1)

去除的系数：`a`, `b`, `c`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+(vu)_x+av_{xxx}-bv_{xxt}=0\\
v_t+u_x+vv_x+cu_{xxx}-dv_{xxt}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF073 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(v\cdot u)-\partial_{xxx}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ The Cauchy problem on large time for surface waves type Boussinesq systems II ](https://arxiv.org/src/1511.08824v1)

去除的系数：`\epsilon`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+\epsilon(vu)_x-\epsilon v_{xxx}=0\\
v_t+u_x+\epsilon vv_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF074 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)-\partial_{xxx}(u)=0
\end{cases}
$$

来源：[ The Cauchy problem on large time for surface waves type Boussinesq systems II ](https://arxiv.org/src/1511.08824v1)

去除的系数：`\epsilon`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+\epsilon(u v)_x=0\\
v_t+u_x+\epsilon vv_x-\epsilon u_{xxx}= 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF075 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{xxx}(v)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ The Cauchy problem on large time for surface waves type Boussinesq systems II ](https://arxiv.org/src/1511.08824v1)

去除的系数：`\epsilon`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+\frac{\epsilon}{3} v_{xxx}+\epsilon (u v)_x=0\\
v_t+ u_x+\epsilon vv_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF076 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)-\partial_{xxx}(v)+\partial_{xxxxx}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)-\partial_{xxx}(u)+\partial_{xxxxx}(u)=0
\end{cases}
$$

来源：[ On the well posedness and large-time behavior of higher order Boussinesq system ](https://arxiv.org/src/1712.08452v2)

去除的系数：`a`, `b`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x-av_{xxx}+ b v_{xxxxx}= 0\\
v_t +u_x -au_{xxx} +bu_{xxxxx}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF077 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+u\cdot \partial_{x}(u)+\partial_{xxx}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(v\cdot u)+\partial_{xxx}(u)=0
\end{cases}
$$

来源：[ A note on the existence of traveling-wave solutions to a Boussinesq system ](https://arxiv.org/src/1408.0494v1)

去除的系数：`a`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+uu_x+cv_{xxx}=0\\
v_t+u_x+(v u)_x+au_{xxx}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF078 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)+u\cdot \partial_{x}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Notes on error estimates for Galerkin approximations of the 'classical' Boussinesq system and related hyperbolic problems ](https://arxiv.org/src/1008.4248v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_{t} + v_{x} + \tfrac{1}{2}(u v)_{x} = 0\\
v_{t} + u_{x} + \tfrac{3}{2}vv_{x} + \tfrac{1}{2}uu_{x} - \tfrac{1}{3}v_{xxt} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF079 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Notes on error estimates for Galerkin approximations of the 'classical' Boussinesq system and related hyperbolic problems ](https://arxiv.org/src/1008.4248v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_{t} + v_{x} = 0\\
v_{t} + u_{x} - \tfrac{1}{3}v_{xxt} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF080 · 3变量 · shallow_water

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)+v\cdot \partial_{y}(u)+\partial_{x}(w)-v=0\\
\partial_{t}(v)+u\cdot \partial_{x}(v)+v\cdot \partial_{y}(v)+\partial_{y}(w)+u=0\\
\partial_{t}(w)+u\cdot \partial_{x}(w)+v\cdot \partial_{y}(w)+w\cdot (\partial_{x}(u)+\partial_{y}(v))=0
\end{cases}
$$

来源：[ The nonlinear 2D supercritical inviscid shallow water equations in a rectangle ](https://arxiv.org/src/1503.00283v1)

去除的系数：`f`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+uu_x + vu_y + gw_x -fv= 0\\
v_t+uv_x + vv_y + gw_y + fu= 0\\
w_t+uw_x + vw_y + w(u_x+v_y) = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF081 · 2变量 · shallow_water

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+v\cdot \partial_{x}(v)+\partial_{x}(u)-\partial_{xxx}(u)=0
\end{cases}
$$

来源：[ Local Well-Posedness of the Inviscid Shallow Water Equations with Surface Tension ](https://arxiv.org/src/2608.21704v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u + \partial_x(uv) = 0\\
\partial_t v+ v \partial_x v + \partial_x u - \partial_x^3 u = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF082 · 2变量 · shallow_water

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}((1+u)\cdot v)-(\partial_{xxx}(v)+\partial_{xxt}(u))=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)-(\partial_{xxx}(u)+\partial_{xxt}(v))=0
\end{cases}
$$

来源：[ A high-order regularization of the non-linear shallow water equations with weakly singular shock waves and its approximation by finite volume methods ](https://arxiv.org/src/2606.01200v1)

去除的系数：`a`, `b`, `c`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+[(1+u)v]_x-[av_{xxx}+bu_{xxt}]=0\\
v_t+u_x+vv_x-[cu_{xxx}+d v_{xxt}]=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF083 · 2变量 · shallow_water

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}((1+u)\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)=\partial_{xxx}(u)+\partial_{xxt}(v)+v\cdot \partial_{xxx}(v)
\end{cases}
$$

来源：[ A high-order regularization of the non-linear shallow water equations with weakly singular shock waves and its approximation by finite volume methods ](https://arxiv.org/src/2606.01200v1)

去除的系数：`D`, `\delta`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+[(D+u)v]_x=0\\
v_t+gu_x+vv_x=\delta [gu_{xxx}+v_{xxt}+ vv_{xxx}]
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF084 · 3变量 · shallow_water

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)+v\cdot \partial_{y}(u)+\partial_{x}(w)=0\\
\partial_{t}(v)+u\cdot \partial_{x}(v)+v\cdot \partial_{y}(v)+\partial_{y}(w)=0\\
\partial_{t}(w)+u\cdot \partial_{x}(w)+v\cdot \partial_{y}(w)+w\cdot (\partial_{x}(u)+\partial_{y}(v))=0
\end{cases}
$$

来源：[ Invariant discretization schemes for the shallow-water equations ](https://arxiv.org/src/1201.0498v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t + uu_x +vu_y + w_x = 0\\
v_t + uv_x + vv_y + w_y = 0\\
w_t + uw_x + vw_y + w(u_x+v_y) = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF085 · 3变量 · shallow_water

$$
\begin{cases}
\partial_{t}(u)+v\cdot \partial_{x}(u)+w\cdot \partial_{y}(u)+u\cdot (\partial_{x}(v)+\partial_{y}(w))=0\\
\partial_{t}(v)+v\cdot \partial_{x}(v)+w\cdot \partial_{y}(v)+\partial_{x}(u)-w=0\\
\partial_{t}(w)+v\cdot \partial_{x}(w)+w\cdot \partial_{y}(w)+\partial_{y}(u)+v=0
\end{cases}
$$

来源：[ A linear and nonlinear analysis of the shallow water equations and its impact on boundary conditions ](https://arxiv.org/src/1907.10713v3)

去除的系数：`f`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + vu_x + wu_y + u (v_x + w_y) =0\\
v_t + v v_x + w v_y + u_x - f w =0\\
w_t + v w_x + w w_y + u_y + f v =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF086 · 3变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=w-u\cdot v\\
\partial_{t}(v)-\Delta(v)=w-u\cdot v\\
\partial_{t}(w)-\Delta(w)=u\cdot v-w
\end{cases}
$$

来源：[ Convergence to equilibrium for a degenerate three species reaction-diffusion system ](https://arxiv.org/src/2406.18339v2)

去除的系数：`d_{u}`, `d_{v}`, `d_{w}`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_{t}u - d_{u} \Delta u = w-uv\\
\partial_{t}v - d_{v} \Delta v = w-uv\\
\partial_{t}w - d_{w} \Delta w = uv-w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF087 · 3变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=w-u\cdot v\\
\partial_{t}(v)=w-u\cdot v\\
\partial_{t}(w)-\Delta(w)=u\cdot v-w
\end{cases}
$$

来源：[ Convergence to equilibrium for a degenerate three species reaction-diffusion system ](https://arxiv.org/src/2406.18339v2)

去除的系数：`d_{u}`, `d_{w}`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_{t}u - d_{u} \Delta u = w-uv\\
\partial_{t}v = w-uv\\
\partial_{t}w- d_{w} \Delta w = uv-w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF088 · 3变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=w-u\cdot v\\
\partial_{t}(v)-\Delta(v)=w-u\cdot v\\
\partial_{t}(w)=u\cdot v-w
\end{cases}
$$

来源：[ Convergence to equilibrium for a degenerate three species reaction-diffusion system ](https://arxiv.org/src/2406.18339v2)

去除的系数：`d_v`, `d_{u}`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_{t}u- d_{u} \Delta u = w-uv\\
\partial_{t}v-d_v \Delta v = w-uv\\
\partial_{t}w = uv-w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF089 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(1)+u\cdot (u-1)\cdot (1-u)\cdot (u+v)-u\cdot v\\
\partial_{t}(v)=\partial_{xx}(1)+u\cdot v-v\cdot (u+v)
\end{cases}
$$

来源：[ A case study of multiple wave solutions in a reaction-diffusion system using invariant manifolds and global bifurcations ](https://arxiv.org/src/2008.05628v4)

去除的系数：`D_1u`, `D_2v`, `\alpha`, `\beta`, `\gamma`, `m`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=D_1u_{xx}+u(u-m)(1-u)(u+v)-\alpha uv\\
v_t=D_2v_{xx}+\beta uv-\gamma v(u+v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF090 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u\cdot (u-1)\cdot (1-u)\cdot (u+v)-u\cdot v\\
\partial_{t}(v)=\partial_{xx}(v)+u\cdot v-v\cdot (u+v)
\end{cases}
$$

来源：[ A case study of multiple wave solutions in a reaction-diffusion system using invariant manifolds and global bifurcations ](https://arxiv.org/src/2008.05628v4)

去除的系数：`a`, `b`, `d`, `g`, `m`, `s`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=du_{xx}+su(u-m)(1-u)(u+v)-auv\\
v_t=v_{xx}+buv-gv(u+v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF091 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+1-u-\frac{(u\cdot v)}{1+u^{2}}\\
\partial_{t}(v)=\Delta(v)+u-\frac{(u\cdot v)}{1+u^{2}}
\end{cases}
$$

来源：[ The global existence of solutions and asymptotic stability of a reaction-diffusion system ](https://arxiv.org/src/1711.00976v2)

去除的系数：`\sigma`, `a`, `b`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t}=\Delta u+a-u-\frac{4uv}{1+u^{2}}\\
\frac{\partial v}{\partial t}=( \sigma c) \Delta v+( \sigma b) ( u-\frac{uv}{1+u^{2}})
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF092 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-u^{3}+u^{2}-u-v+1\\
\partial_{t}(v)=\Delta(v)+u-v
\end{cases}
$$

来源：[ The global existence of solutions and asymptotic stability of a reaction-diffusion system ](https://arxiv.org/src/1711.00976v2)

去除的系数：`I`, `\beta`, `\gamma`, `\varepsilon`, `d_{1}`, `d_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t}=d_{1}\Delta u-u^{3}+( 1+\beta ) u^{2}-\beta u-v+I\\
\frac{\partial v}{\partial t}=d_{2}\Delta v+\varepsilon u-\varepsilon \gamma v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF093 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=u+v\\
\partial_{t}(v)-\Delta(v)=u-v
\end{cases}
$$

来源：[ Entropy methods and convergence to equilibrium for volume-surface reaction-diffusion systems ](https://arxiv.org/src/1609.05943v2)

去除的系数：`\alpha`, `\beta`, `d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
u_t - d_u\Delta u = -\beta u + \alpha v\\
v_t - d_v\Delta v = \beta u - \alpha v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF094 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta((1+u+v)\cdot u)+u\cdot (1-u-1)\\
\partial_{t}(v)=\Delta((1+u+v)\cdot v)+v\cdot (1-1-v)
\end{cases}
$$

来源：[ Coexisting steady-state solutions of a class of reaction-diffusion systems with different boundary conditions ](https://arxiv.org/src/2404.12664v1)

去除的系数：`a_1v`, `a_2u`, `a_{11}`, `a_{12}`, `a_{21}`, `a_{22}`, `d_{1}`, `d_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t}=\Delta[(d_{1}+a_{11}u+a_{12} v)u]+u(1-u-a_1v)\\
\frac{\partial v}{\partial t}=\Delta[(d_{2}+a_{21}u+a_{22} v)v]+v(1-a_2u-v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF095 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-u\cdot v\\
\partial_{t}(v)=\Delta(v)-u\cdot v
\end{cases}
$$

来源：[ Fast reaction limit of reaction-diffusion systems ](https://arxiv.org/src/1901.04278v1)

去除的系数：`d_1`, `d_2`, `k`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = d_1 \Delta u -kuv\\
\frac{\partial v}{\partial t} = d_2 \Delta v -kuv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF096 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=u-u^{3}-v+\Delta(u)\\
\partial_{t}(v)=u-(1+\sin(1)\cdot t)\cdot v+\Delta(v)
\end{cases}
$$

来源：[ Resonance tongues and patterns in periodically forced reaction-diffusion systems ](https://arxiv.org/src/nlin/0401031v1)

去除的系数：`\delta`, `\epsilon`, `\gamma`, `\omega_f`, `a_1`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = u - u^3 - v + \nabla^2 u\\
v_t = \epsilon [ u - (a_1 + \gamma \sin\omega_f t) v ] + \delta\nabla^2 v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF097 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+v\cdot u-u\\
\partial_{t}(v)=\Delta(v)-v\cdot u-v+r
\end{cases}
$$

来源：[ Energetic Derivation and Geometric Reduction of Reaction-Diffusion Systems with Holling-Type Functional Responses ](https://arxiv.org/src/2507.06319v1)

去除的系数：`a_0`, `d_u`, `d_{v}`, `m_u`, `m_v`, `p_1`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u= d_u\Delta u + p_1 vu -m_u u\\
\partial_t v= d_{v}\Delta v- p_1 vu -m_v v+ ra_0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF098 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+v\cdot u^{2}-u\\
\partial_{t}(v)=\Delta(v)-v\cdot u^{2}-v+r
\end{cases}
$$

来源：[ Energetic Derivation and Geometric Reduction of Reaction-Diffusion Systems with Holling-Type Functional Responses ](https://arxiv.org/src/2507.06319v1)

去除的系数：`a_0`, `d_u`, `d_{v}`, `m_u`, `m_v`, `p_1`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u= d_u\Delta u + p_1 vu^2 -m_u u\\
\partial_t v= d_{v}\Delta v- p_1 vu^2 -m_v v+ ra_0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF099 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\cdot (1-u)-\frac{(u\cdot v)}{u+1}\\
\partial_{t}(v)=\Delta(v)+\frac{(u\cdot v)}{u+1}-v
\end{cases}
$$

来源：[ An Observer for an Occluded Reaction-Diffusion System With Spatially Varying Parameters ](https://arxiv.org/src/1702.07693v1)

去除的系数：`h`, `k`, `m`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \triangle u + u(1-u) - \frac{u v}{u + h}\\
\frac{\partial v}{\partial t} = \triangle v + k\frac{u v}{u+h} - mv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF100 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u\cdot (1-u-v)\\
\partial_{t}(v)=\partial_{xx}(v)+v\cdot (3-u-v)
\end{cases}
$$

来源：[ A Numerical Study of WENO Approximations to Sharp Propagating Fronts for Reaction-Diffusion Systems ](https://arxiv.org/src/2407.09393v1)

去除的系数：`D`, `\rho`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = D \frac{\partial^2 u}{\partial x^2} + \rho u ( 1-u-v )\\
\frac{\partial v}{\partial t} = \frac{D}{3} \frac{\partial^2 v}{\partial x^2} + \rho v ( 3-4u-v )
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF101 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=0\\
\partial_{t}(v)=u-v
\end{cases}
$$

来源：[ Well-posedness and exponential equilibration of a volume-surface reaction-diffusion system with nonlinear boundary coupling ](https://arxiv.org/src/1404.2809v2)

去除的系数：`\delta_u`

<details><summary>对应原式与处理记录</summary>

```latex
u_t - \delta_u \Delta u = 0\\
v_t = u - v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF102 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+1-u+u^{2}\cdot v\\
\partial_{t}(v)=\Delta(v)+1-u^{2}\cdot v
\end{cases}
$$

来源：[ Classification of parameter spaces for reaction-diffusion systems on stationary domains ](https://arxiv.org/src/1701.05164v1)

去除的系数：`\alpha`, `\beta`, `\gamma`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = \triangle u + \gamma (\alpha -u+u^2v)\\
\frac{\partial v}{\partial t} = d \triangle v + \gamma( \beta - u^2v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF103 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=u-u^{3}-v+\partial_{xx}(u)\\
\partial_{t}(v)=u
\end{cases}
$$

来源：[ Qualitative Analysis of certain Reaction-Diffusion Systems of the FitzHugh-Nagumo type ](https://arxiv.org/src/1903.05754v3)

去除的系数：`\alpha`

<details><summary>对应原式与处理记录</summary>

```latex
u_t= \alpha u-u^3-v+u_{xx}\\
v_t= u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF104 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=u-v+\partial_{xx}(u)\\
\partial_{t}(v)=u
\end{cases}
$$

来源：[ Qualitative Analysis of certain Reaction-Diffusion Systems of the FitzHugh-Nagumo type ](https://arxiv.org/src/1903.05754v3)

去除的系数：`\alpha`

<details><summary>对应原式与处理记录</summary>

```latex
u_t= \alpha u-v+u_{xx}\\
v_t= u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF105 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u-u^{3}-(v+1)\\
\partial_{t}(v)=\partial_{xx}(v)-v+u
\end{cases}
$$

来源：[ Travelling front solutions in a spatially heterogeneous reaction-diffusion system ](https://arxiv.org/src/2507.21797v2)

去除的系数：`\alpha`, `\gamma`, `\tau`, `\varepsilon`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = \varepsilon^2\partial_x^2 u + u - u^3 - \varepsilon(\alpha v +\gamma)\\
\tau \partial_t v = \partial_x^2 v-v +u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF106 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-u+\frac{(u^{2})}{v\cdot (1+u^{2})}\\
\partial_{t}(v)=\Delta(v)-v+\frac{(u^{2})}{\sqrt(1)}
\end{cases}
$$

来源：[ Approximation Theory of Laplacian-Based Neural Operators for Reaction-Diffusion System ](https://arxiv.org/src/2605.12025v2)

去除的系数：`\sigma`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = d_1\Delta u - u + \frac{u^2}{v(1+\sigma u^2)}\\
v_t = d_2\Delta v - v + \frac{u^2}{\sqrt{d_1}}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF107 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=u\\
\partial_{t}(v)-\Delta(v)=u
\end{cases}
$$

来源：[ Convergence to the complex balanced equilibrium for some chemical reaction-diffusion systems with boundary equilibria ](https://arxiv.org/src/1812.07707v1)

去除的系数：`d_u`, `d_v`, `k`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-d_u\Delta u= -ku\\
v_t-d_v\Delta v=ku
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF108 · 3变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=u\cdot v\\
\partial_{t}(v)-\Delta(v)=u\cdot v\\
\partial_{t}(w)-\Delta(w)=u\cdot v
\end{cases}
$$

来源：[ Convergence to the complex balanced equilibrium for some chemical reaction-diffusion systems with boundary equilibria ](https://arxiv.org/src/1812.07707v1)

去除的系数：`d_u`, `d_v`, `d_w`, `k`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-d_u\Delta u= -kuv\\
v_t-d_v\Delta v=-kuv\\
w_t-d_w\Delta w=kuv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF109 · 3变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\partial_{xx}(u)=(-u)\cdot v^{2}+v\cdot w\\
\partial_{t}(v)-\partial_{xx}(v)=(-u)\cdot v^{2}+v\cdot w\\
\partial_{t}(w)-\partial_{xx}(w)=u\cdot v^{2}-v\cdot w
\end{cases}
$$

来源：[ Convergence to the complex balanced equilibrium for some chemical reaction-diffusion systems with boundary equilibria ](https://arxiv.org/src/1812.07707v1)

去除的系数：`d_u`, `d_v`, `d_w`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-d_u u_{xx}=-uv^2+vw\\
v_t-d_v v_{xx}=-uv^2+vw\\
w_t-d_w w_{xx}=uv^2-vw
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF110 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=-u^{2}+u\cdot v\\
\partial_{t}(v)-\Delta(v)=u^{2}-u\cdot v
\end{cases}
$$

来源：[ Explicit exponential convergence to equilibrium for nonlinear reaction-diffusion systems with detailed balance condition ](https://arxiv.org/src/1601.05992v3)

去除的系数：`d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
u_t - d_u\Delta u = -u^2 + uv\\
v_t - d_v\Delta v = u^2 - uv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF111 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)-u\cdot v^{2}+v\\
\partial_{t}(v)=\partial_{xx}(v)+u\cdot v^{2}-v+1-v
\end{cases}
$$

来源：[ Pattern selection in reaction diffusion systems ](https://arxiv.org/src/2005.07940v2)

去除的系数：`D_u`, `D_v`, `\beta`, `\delta`, `\gamma`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = D_u \frac{\partial^2 u}{\partial x^2} - \beta uv^2 + \gamma v\\
\frac{\partial v}{\partial t} = D_v \frac{\partial^2 v}{\partial x^2} + \beta uv^2 - \gamma v + \delta c -\delta v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF112 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\partial_{x}(u\cdot \partial_{x}(u+v))-\partial_{x}(u)\\
\partial_{t}(v)=\partial_{x}(v\cdot \partial_{x}(u+v))+\partial_{x}(v)
\end{cases}
$$

来源：[ Global solutions to cross-diffusion systems with independent advections in one dimension ](https://arxiv.org/src/2603.20153v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = \partial_x(u \partial_x(u+v)) - \partial_x u\\
\partial_t v = \partial_x(v \partial_x(u+v)) + \partial_x v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF113 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\nabla\cdot(u\cdot v\cdot \nabla(u))-\nabla\cdot(\frac{(u^{2}\cdot v)}{(1+v)^{2}}\cdot \nabla(v))+u\cdot v\\
\partial_{t}(v)=\Delta(v)-u\cdot v
\end{cases}
$$

来源：[ Derivation of a bacterial nutrient-taxis system with doubly degenerate cross-diffusion as the parabolic limit of a velocity-jump process ](https://arxiv.org/src/1711.03015v1)

去除的系数：`\chi_0`, `\sigma_0`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \nabla \cdot ( \sigma_0 uv \nabla u) - \nabla \cdot (\sigma_0 \chi_0 \frac{u^2 v}{(1+v)^2}\nabla v ) + uv\\
v_t = \Delta v - uv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF114 · 4变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+\nabla\cdot(u\cdot \nabla(w))\\
\partial_{t}(v)=\Delta(v)+\nabla\cdot(v\cdot \nabla(p))\\
\partial_{t}(w)=-w+\frac{(v)}{1+v}\\
\partial_{t}(p)=-p+\frac{(u)}{1+u}
\end{cases}
$$

来源：[ A cross-diffusion system modelling rivaling gangs: global existence of bounded solutions and FCT stabilization for numerical simulation ](https://arxiv.org/src/2312.08147v1)

去除的系数：`D_u`, `D_v`, `\chi_u`, `\chi_v`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = D_u \Delta u + \chi_u \nabla \cdot (u \nabla w)\\
v_t = D_v \Delta v + \chi_v \nabla \cdot (v \nabla p)\\
w_t = -w + \frac{v}{1+v}\\
p_t = -p + \frac{u}{1+u}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF115 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=(-u)\cdot v\\
\partial_{t}(v)=u\cdot v-v-\partial_{xx}(u)
\end{cases}
$$

来源：[ On Persistence and Stability of some Biological Systems with Cross Diffusion ](https://arxiv.org/src/nlin/0404021v1)

去除的系数：`D`, `\lambda`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t}=-uv\\
\frac{\partial v}{\partial t}=uv-\lambda v-D\frac{\partial ^{2}u}{\partial x^{2}}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF116 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta((1+u+v)\cdot u)+u\\
\partial_{t}(v)=\Delta((1+u+v)\cdot v)+v
\end{cases}
$$

来源：[ Self-diffusion and cross-diffusion equations: $w^{1,p}$-estimates and global existence of smooth solutions ](https://arxiv.org/src/1311.6828v1)

去除的系数：`a_1`, `a_2`, `a_{11}`, `a_{12}`, `a_{21}`, `a_{22}`, `b_1u`, `b_2u`, `c_1v`, `c_2v`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \Delta[(d_1 + a_{11} u + a_{12} v)u] + u(a_1- b_1u-c_1v)\\
v_t = \Delta[(d_2 + a_{21}u + a_{22}v)v] + v(a_2-b_2u-c_2v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF117 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta((1+u+v)\cdot u)+u\\
\partial_{t}(v)=\Delta((1+v)\cdot v)+v
\end{cases}
$$

来源：[ Self-diffusion and cross-diffusion equations: $w^{1,p}$-estimates and global existence of smooth solutions ](https://arxiv.org/src/1311.6828v1)

去除的系数：`a_1`, `a_2`, `a_{11}`, `a_{12}`, `a_{22}`, `b_1u`, `b_2u`, `c_1v`, `c_2v`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \Delta[(d_1 + a_{11} u + a_{12} v)u] + u(a_1- b_1u-c_1v)\\
v_t = \Delta[(d_2 + a_{22}v)v] + v(a_2-b_2u-c_2v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF118 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\nabla\cdot((1+u+v)\cdot \nabla(u)+u\cdot \nabla(v))+u\cdot (1-u-1)\\
\partial_{t}(v)=\nabla\cdot((1+v)\cdot \nabla(v))+v-v
\end{cases}
$$

来源：[ Self-diffusion and cross-diffusion equations: $w^{1,p}$-estimates and global existence of smooth solutions ](https://arxiv.org/src/1311.6828v1)

去除的系数：`a_1`, `a_2`, `a_{11}`, `a_{12}`, `a_{22}`, `b_1`, `b_2u`, `c_1v`, `c_2v`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \nabla\cdot[(d_1 + 2a_{11}u + a_{12}v)\nabla u + a_{12} u \nabla v ] + u(a_1 -b_1 u - c_1v)\\
v_t = \nabla\cdot[(d_2 + 2a_{22}v) \nabla v] + v(a_2 - c_2v) -b_2u v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF119 · 2变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)=\Delta((1+v)\cdot u)+u\cdot (1-u-v)\\
\partial_{t}(v)=\Delta((1+u)\cdot v)+v\cdot (1-u-v)
\end{cases}
$$

来源：[ The existence and instability of blowing-up steady states for the Shigesada-Kawasaki-Teramoto competition model with cross-diffusion ](https://arxiv.org/src/2511.15039v1)

去除的系数：`\alpha`, `\beta`, `a_{1}`, `a_{2}`, `b_{1}`, `b_{2}`, `c_{1}`, `c_{2}`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=d_1\Delta[(1+\alpha v)u]+u(a_{1}-b_{1}u-c_{1}v)\\
v_{t}=d_2\Delta[(1+\beta u)v]+v(a_{2}-b_{2}u-c_{2}v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF120 · 2变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)=\Delta((1+v)\cdot u)+u\cdot (1-u)\\
\partial_{t}(v)=\Delta((1+u)\cdot v)+v\cdot (1-u)
\end{cases}
$$

来源：[ The existence and instability of blowing-up steady states for the Shigesada-Kawasaki-Teramoto competition model with cross-diffusion ](https://arxiv.org/src/2511.15039v1)

去除的系数：`\beta`, `a_{1}`, `a_{2}`, `b_{1}`, `b_{2}`, `d_{1}`, `d_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=d_{1}\Delta[(1+v)u]+u(a_{1}-b_{1}u)\\
v_{t}=d_{2}\Delta[(1+\beta u)v]+v(a_{2}-b_{2}u)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF121 · 4变量 · haptotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+u\cdot (1-u)-u\cdot p\\
\partial_{t}(v)=(-(u+w))\cdot v\\
\partial_{t}(w)=\Delta(w)-w+u\cdot p\\
\partial_{t}(p)=\Delta(p)-p-u\cdot p+w
\end{cases}
$$

来源：[ Asymptotic behavior of a doubly haptotactic cross-diffusion model for oncolytic virotherapy ](https://arxiv.org/src/2111.08378v1)

去除的系数：`D_p`, `D_w`, `D_{u}`, `\alpha_u`, `\alpha_w`, `\beta`, `\mu_u`, `\rho`, `\xi_u`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=D_{u}\Delta u-\xi_u\nabla \cdot(u\nabla v)+\mu_u u(1-u)-\rho up\\
v_{t}=-(\alpha_u u+\alpha_w w)v\\
w_{t}=D_w\Delta w-w +up\\
p_{t}=D_p\Delta p-p-up+\beta w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF122 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(w))-u\cdot v\\
\partial_{t}(v)=\Delta(v)+u\cdot v-v\\
\partial_{t}(w)=\Delta(w)+u-w
\end{cases}
$$

来源：[ Determining habitat anomalies in cross-diffusion predator-prey chemotaxis models ](https://arxiv.org/src/2512.22946v1)

去除的系数：`\chi`, `a`, `b`, `c`, `d`, `d_u`, `d_v`, `d_w`, `e`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = d_u \Delta u - \chi \nabla \cdot (u \nabla w) - a u v\\
\partial_t v = d_v \Delta v + b u v - c v\\
\partial_t w = d_w \Delta w + d u - e w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF123 · 2变量 · cross_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+v-u\\
\partial_{t}(v)=\Delta(v)+\Delta(u)
\end{cases}
$$

来源：[ Slow Manifolds for PDE with Fast Reactions and Small Cross Diffusion ](https://arxiv.org/src/2501.16775v1)

去除的系数：`\delta`, `\varepsilon`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u= (d+\delta)\Delta u+\frac{1}{\varepsilon}(v-2u)\\
\partial_t v= d\Delta v +\delta \Delta u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF124 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+\nabla\cdot(u\cdot \nabla(w))+r\cdot u-u^{2}\\
\partial_{t}(v)=\Delta(v)+u-v\\
\partial_{t}(w)=\Delta(w)+u-w
\end{cases}
$$

来源：[ Determining a parabolic-elliptic-elliptic system by boundary observation of its non-negative solutions under chemotaxis background ](https://arxiv.org/src/2509.04850v2)

去除的系数：`\alpha`, `\beta`, `\chi`, `\delta`, `\gamma`, `\mu`, `\tau`, `\xi`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = \Delta u - \nabla \cdot (\chi u \nabla v) + \nabla \cdot (\xi u\nabla w) + r u - \mu u^2\\
\tau \partial_t v = \Delta v + \alpha u - \beta v\\
\tau \partial_t w = \Delta w + \gamma u - \delta w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF125 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(\frac{(u)}{v}\cdot \nabla(v))\\
\partial_{t}(v)=\Delta(v)-v+u
\end{cases}
$$

来源：[ Boundedness to a logistic chemotaxis system with singular sensitivity ](https://arxiv.org/src/2003.03016v1)

去除的系数：`\chi`, `\tau`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u-\chi\nabla\cdot(\frac{u}{v}\nabla v)\\
\tau v_t=\Delta v-v+u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF126 · 4变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v\cdot w))+u\cdot (1-u+1+1)\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(p))+v\cdot (1-v-1+1)\\
\partial_{t}(w)=\Delta(w)+\nabla\cdot(w\cdot \nabla(p))+w\cdot (1-w-1-1)\\
\partial_{t}(p)=\Delta(p)+v+w-p
\end{cases}
$$

来源：[ The simultaneous effect of chemotaxis and alarm-taxis on the global existence and stability of a predator-prey system ](https://arxiv.org/src/2510.14728v2)

去除的系数：`\alpha`, `\beta`, `\chi_1`, `\chi_2`, `\gamma`, `\mu_1`, `\mu_2`, `\mu_3`, `\xi`, `a_1v`, `a_2w`, `a_3u`, `a_4w`, `a_5u`, `a_6v`, `d_1`, `d_2`, `d_3`, `d_4`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=d_1\Delta u-\chi_1\nabla\cdot(u\nabla(vw))+\mu_1 u(1- u+a_1v+a_2w)\\
v_t=d_2\Delta v-\chi_2\nabla\cdot(v\nabla p)+\mu_2 v(1-v-a_3u+a_4w)\\
w_t=d_3\Delta w+\xi\nabla\cdot(w\nabla p)+\mu_3 w(1-w-a_5u-a_6v)\\
p_{t}=d_4\Delta p+\alpha v+\beta w-\gamma p
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF127 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(u))+v\\
\partial_{t}(w)=\Delta(w)-\nabla\cdot(w\cdot \nabla(u\cdot v))+w
\end{cases}
$$

来源：[ The simultaneous effect of chemotaxis and alarm-taxis on the global existence and stability of a predator-prey system ](https://arxiv.org/src/2510.14728v2)

去除的系数：`\chi`, `\lambda_1`, `\lambda_2`, `\lambda_3`, `\mu_1u`, `\mu_2u`, `\mu_3w`, `\xi`, `a_1v`, `a_2w`, `a_3w`, `b_1u`, `b_2u`, `b_3v`, `d_1`, `d_2`, `d_3`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=d_1\Delta u+u(\lambda_1-\mu_1u-a_1v-a_2w)\\
v_t=d_2\Delta v-\xi\nabla\cdot(v\nabla u)+v(\lambda_2-\mu_2u+b_1u-a_3w)\\
w_t=d_3\Delta w-\chi\nabla\cdot(w\nabla(uv))+w(\lambda_3-\mu_3w+b_2u+b_3v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF128 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\cdot (1-u)-1-\frac{(u\cdot w)}{u+w}\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(u))+1-v+u\cdot v-1\\
\partial_{t}(w)=\Delta(w)-\nabla\cdot(w\cdot \nabla(u\cdot v))+1-w+v\cdot w+\frac{(u\cdot w)}{u+w}
\end{cases}
$$

来源：[ The simultaneous effect of chemotaxis and alarm-taxis on the global existence and stability of a predator-prey system ](https://arxiv.org/src/2510.14728v2)

去除的系数：`\chi`, `\mu_1`, `\mu_2v`, `\mu_3w`, `\xi`, `b_1uv`, `b_2vw`, `b_3`, `c_3`, `d_1`, `d_2`, `d_3`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=d_1\Delta u+\mu_1 u(1-u)-b_1uv-b_3\frac{uw}{u+w}\\
v_t=d_2\Delta v-\xi\nabla\cdot(v\nabla u)+\mu_2v(1-v)+uv-b_2vw\\
w_t=d_3\Delta w-\chi\nabla\cdot(w\nabla(uv))+\mu_3w(1-w)+vw+c_3\frac{uw}{u+w}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF129 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\cdot (1-u)-1\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(u))+1-v+u\cdot v-1\\
\partial_{t}(w)=\Delta(w)-\nabla\cdot(w\cdot \nabla(u\cdot v))+1-w+v\cdot w
\end{cases}
$$

来源：[ The simultaneous effect of chemotaxis and alarm-taxis on the global existence and stability of a predator-prey system ](https://arxiv.org/src/2510.14728v2)

去除的系数：`\chi`, `\theta_1v`, `\theta_2w`, `\xi`, `b_1uv`, `b_2vw`, `d_1`, `d_2`, `d_3`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=d_1\Delta u+u(1-u)-b_1uv\\
v_t=d_2\Delta v-\xi\nabla\cdot(v\nabla u)+\theta_1v(1-v)+uv-b_2vw\\
w_t=d_3\Delta w-\chi\nabla\cdot(w\nabla(uv))+\theta_2w(1-w)+vw
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF130 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\cdot (1-u-\frac{(v)}{v+1})\\
\partial_{t}(v)=\Delta(v)+v\cdot (\frac{(u)}{v+1}-1-\frac{(w)}{w+1})\\
\partial_{t}(w)=\Delta(w)-\nabla\cdot(w\cdot \nabla(u\cdot v))+w\cdot (\frac{(v)}{w+1}-1)
\end{cases}
$$

来源：[ The simultaneous effect of chemotaxis and alarm-taxis on the global existence and stability of a predator-prey system ](https://arxiv.org/src/2510.14728v2)

去除的系数：`\alpha`, `\beta`, `\chi`, `\rho`, `\sigma`, `a`, `b`, `c`, `d_1`, `d_2`, `d_3`, `m`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=d_1\Delta u+u(1-u-\frac{av}{v+\rho})\\
v_t=d_2\Delta v+v(\frac{bu}{v+\rho}-\alpha-\frac{cw}{w+\sigma})\\
w_t=d_3\Delta w-\chi\nabla\cdot(w\nabla(uv))+w(\frac{mv}{w+\sigma}-\beta)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF131 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(w))+u\cdot (1-u-v)\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(w))+v\cdot (1-1-v)\\
\partial_{t}(w)=\Delta(w)+u+v-w
\end{cases}
$$

来源：[ Boundedness and stabilization in a two-species chemotaxis-competition system of parabolic-parabolic-elliptic type ](https://arxiv.org/src/1703.08389v1)

去除的系数：`\alpha`, `\beta`, `\chi_1`, `\chi_2`, `\gamma`, `\mu_1`, `\mu_2`, `\tau`, `a_1`, `a_2u`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\Delta u - \chi_1\nabla \cdot (u \nabla w) +\mu_1 u(1-u-a_1 v)\\
v_t=\Delta v - \chi_2\nabla \cdot (v \nabla w) +\mu_2 v(1-a_2u-v)\\
\tau w_t = \Delta w + \alpha u + \beta v - \gamma w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF132 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)-\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)-\partial_{x}(u)=0
\end{cases}
$$

来源：[ Nonlinear stability of composite waves of traveling wave and rarefaction wave for a parabolic-hyperbolic system arising from chemotaxis ](https://arxiv.org/src/2609.23448v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t-(uv)_x=0\\
v_t-u_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF133 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(\frac{(u)}{v}\cdot \nabla(v))\\
\partial_{t}(v)=\Delta(v)-u\cdot v
\end{cases}
$$

来源：[ Eventual smoothness of generalized solutions to a singular chemotaxis-Stokes system ](https://arxiv.org/src/1705.06131v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=\Delta u-\nabla\cdot(\frac{u}{v}\nabla v)\\
v_{t}=\Delta v-uv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF134 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+r\cdot u-u^{2}\\
\partial_{t}(v)=\Delta(v)+u-v
\end{cases}
$$

来源：[ Asymptotics and periodic dynamics in a negative chemotaxis system with cell lethality ](https://arxiv.org/src/2511.06889v1)

去除的系数：`D_1`, `D_2`, `\alpha`, `\chi`, `\mu`, `\tau`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = D_1 \Delta u - \chi \nabla \cdot (u \nabla v) + ru- \mu u^2\\
\tau \frac{\partial v}{\partial t} = D_2 \Delta v + u -\alpha v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF135 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)=u\cdot \partial_{x}(w)-v\\
\partial_{t}(w)=\partial_{xx}(w)+u-w
\end{cases}
$$

来源：[ Global solutions for a chemotaxis hyperbolic-parabolic system on networks with nonhomogeneous boundary conditions ](https://arxiv.org/src/1809.04623v1)

去除的系数：`D`, `\beta`, `\lambda`, `a`, `b`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_tu +\lambda\partial_x v=0\\
\partial_t v +\lambda \partial_x u= u \partial_x w -\beta v\\
\partial_t w= D\partial_{xx} w +a u -bw
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF136 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(w))+u\cdot (1-u-1)\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(w))+v\cdot (1-v-1)\\
\partial_{t}(w)=\Delta(w)+u+v-w
\end{cases}
$$

来源：[ Transient instability and recurrent aggregation in a two-species chemotaxis-competition system under environmental periodicity ](https://arxiv.org/src/2608.07701v1)

去除的系数：`\alpha`, `\beta`, `\chi_1`, `\chi_2`, `\mu_1`, `\mu_2`, `\tau`, `a_1v`, `a_2u`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = d_1 \Delta u - \chi_1 \nabla \cdot (u \nabla w) + \mu_1 u (1-u-a_1v)\\
\frac{\partial v}{\partial t} = d_2 \Delta v - \chi_2 \nabla \cdot (v \nabla w) + \mu_2 v (1-v-a_2u)\\
\tau \frac{\partial w}{\partial t}= \Delta w + \alpha u + \beta v - w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF137 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\Delta(v)\\
\partial_{t}(v)=\Delta(v)+u-v
\end{cases}
$$

来源：[ Parameter Identification in Reaction-Diffusion-Chemotaxis Systems from Single Turing Pattern Amplitudes ](https://arxiv.org/src/2509.07458v2)

去除的系数：`\chi_0`, `d_u`, `d_v`, `h`, `p`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=d_u \Delta u-\chi_0\Delta v\\
\partial_t v=d_v \Delta v+hu-pv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF138 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+r\cdot u\cdot (1-u)\\
\partial_{t}(v)=\Delta(v)+u-v
\end{cases}
$$

来源：[ Parameter Identification in Reaction-Diffusion-Chemotaxis Systems from Single Turing Pattern Amplitudes ](https://arxiv.org/src/2509.07458v2)

去除的系数：`\chi_0`, `d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=d_u \Delta u-\chi_0 \nabla\cdot (u \nabla v)+ru(1-u)\\
\partial_t v=d_v \Delta v +u-v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF139 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(\frac{(u)}{v}\cdot \nabla(v))+r\cdot u\cdot (1-u)\\
\partial_{t}(v)=\Delta(v)+u-v
\end{cases}
$$

来源：[ Parameter Identification in Reaction-Diffusion-Chemotaxis Systems from Single Turing Pattern Amplitudes ](https://arxiv.org/src/2509.07458v2)

去除的系数：`\chi_0`, `d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=d_u \Delta u-\chi_0 \nabla \cdot(\frac{u}{v} \nabla v)+ru(1-u)\\
\partial_t v=d_v \Delta v +u-v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF140 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(v))+\nabla\cdot(u\cdot \nabla(w))\\
\partial_{t}(v)=\Delta(v)-u\cdot v\\
\partial_{t}(w)=\Delta(w)-u\cdot w
\end{cases}
$$

来源：[ Uniform in time $L^\infty$-estimates for an attraction-repulsion chemotaxis system with double saturation ](https://arxiv.org/src/2106.07038v2)

去除的系数：`\chi`, `\xi`

<details><summary>对应原式与处理记录</summary>

```latex
u_t= \Delta u - \chi \nabla \cdot (u \nabla v)+\xi \nabla \cdot (u \nabla w)\\
v_t=\Delta v- uv\\
w_t= \Delta w- uw
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF141 · 2变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\cdot (1-u-v)\\
\partial_{t}(v)=\Delta(v)+v\cdot (1-v-u)
\end{cases}
$$

来源：[ Two-species competition model with chemotaxis: well-posedness, stability and dynamics ](https://arxiv.org/src/2105.08272v1)

去除的系数：`a_1`, `a_2`, `b_1`, `b_2`, `d_1`, `d_2`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u = d_1\Delta u + b_1 u(1- u- a_1 v)\\
\partial_t v = d_2 \Delta v + b_2 v(1 -v - a_2 u)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF142 · 3变量 · chemotaxis

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\nabla\cdot(u\cdot \nabla(w))+w-u^{2}\\
\partial_{t}(v)=\Delta(v)-\nabla\cdot(v\cdot \nabla(w))+w+r\cdot u\cdot v-1^{2}\\
\partial_{t}(w)=\Delta(w)+u+v-w
\end{cases}
$$

来源：[ Global boundedness and asymptotic behavior of the chemotaxis system for Alopecia Areata with weakly singular sensitivity ](https://arxiv.org/src/2604.26905v1)

去除的系数：`\chi_1`, `\chi_2`, `\mu_1`, `\mu_2v`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = \Delta u - \chi_1\nabla \cdot (u \nabla w) +w - \mu_1 u^2\\
v_t = \Delta v - \chi_2\nabla \cdot (v \nabla w) +w+ruv -\mu_2v^2\\
w_t=\Delta w+u+v-w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF143 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(v)+\partial_{x}(u\cdot v)\\
\partial_{t}(v)=\partial_{x}(u)+v\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ Solitary-wave solutions to a dual equation of the Kaup-Boussinesq system ](https://arxiv.org/src/0910.3126v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=v_{xxx}+2(uv)_x\\
v_t=u_x+2vv_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF144 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)+\frac{(1)}{r^{2}}\cdot \partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(u\cdot v)=0
\end{cases}
$$

来源：[ Surface Wave Solutions in 1D and 2D for the Broer-Kaup-Boussinesq-Kupershmidt (BKBK) System ](https://arxiv.org/src/2510.02577v1)

去除的系数：`F`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+u u_x + \frac{1}{Fr^2}v_x =0\\
v_t+(u v)_x =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF145 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)=-\partial_{x}(u^{2}+v+\partial_{x}(u))\\
\partial_{t}(v)=-\partial_{x}(u\cdot v+\partial_{xx}(u)-\partial_{x}(v))
\end{cases}
$$

来源：[ Surface Wave Solutions in 1D and 2D for the Broer-Kaup-Boussinesq-Kupershmidt (BKBK) System ](https://arxiv.org/src/2510.02577v1)

去除的系数：`\alpha`, `\beta`

<details><summary>对应原式与处理记录</summary>

```latex
u_t =-(u^2 / 2+v+\beta u_x)_x\\
v_t =-(u v +\alpha u_{x x}-\beta v_x)_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF146 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)-\partial_{xxt}(v)-\partial_{xx}(v)=0
\end{cases}
$$

来源：[ Oscillatory and regularized shock waves for a dissipative Peregrine-Boussinesq system ](https://arxiv.org/src/2209.10129v2)

去除的系数：`D`, `\varepsilon`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + Dv_x + (u v)_x = 0\\
v_t + gu_x + vv_x - \frac{D^2}{3} v_{xxt} - \varepsilon v_{xx} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF147 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)+\partial_{xxx}(v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Extended water wave systems of Boussinesq equations on a finite interval: Theory and numerical analysis ](https://arxiv.org/src/2210.03279v1)

去除的系数：`\varepsilon`, `a`, `b`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+\varepsilon (u v)_x+\varepsilon (a v_{xxx}-b u_{xxt}) = 0\\
v_t+u_x+\varepsilon vv_x -\varepsilon dv_{xxt}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF148 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{xxx}(v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Extended water wave systems of Boussinesq equations on a finite interval: Theory and numerical analysis ](https://arxiv.org/src/2210.03279v1)

去除的系数：`\varepsilon`, `a`, `b`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x + \varepsilon (a v_{xxx} - b u_{xxt}) = 0\\
v_t + u_x - \varepsilon d v_{xxt} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF149 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)-\partial_{xxx}(v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Extended water wave systems of Boussinesq equations on a finite interval: Theory and numerical analysis ](https://arxiv.org/src/2210.03279v1)

去除的系数：`\alpha`, `\beta`, `\delta`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x - \alpha v_{xxx} - \beta u_{xxt} = 0\\
v_t + u_x - \delta v_{xxt} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF150 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)-\partial_{xxx}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Extended water wave systems of Boussinesq equations on a finite interval: Theory and numerical analysis ](https://arxiv.org/src/2210.03279v1)

去除的系数：`\alpha`, `\delta`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x - \alpha v_{xxx} = 0\\
v_t + u_x - \delta v_{xxt} = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF151 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)+\partial_{xxx}(u)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Spectral Jacobi approximations for Boussinesq systems ](https://arxiv.org/src/2312.05559v1)

去除的系数：`b`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}+v_{x}+(u v)_{x}-bu_{xxt}=0\\
v_{t}+u_{x}+vv_{x}+cu_{xxx}-bv_{xxt}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF152 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+u\cdot \partial_{x}(u)=0\\
\partial_{t}(v)+\partial_{x}(u\cdot v)+\partial_{xxx}(u)=0
\end{cases}
$$

来源：[ Multi-lump, lump-kink and interaction of breather with other nonlinear waves of a couple Boussinesq system ](https://arxiv.org/src/2504.21506v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t +v_x +2uu_x =0\\
v_t +2(uv)_x +u_{xxx}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF153 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)+\partial_{xxx}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)+\partial_{x}(v^{2})+\partial_{xxx}(u)=0
\end{cases}
$$

来源：[ Well-posednesss of strongly dispersive two-dimensional surface waves Boussinesq systems ](https://arxiv.org/src/1103.4159v2)

去除的系数：`\epsilon`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x+\epsilon(u v)_x+\epsilon v_{xxx}=0\\
v_t + u_x +\frac{\epsilon}{2} (v^2)_x+\epsilon u_{xxx}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF154 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)-\partial_{xxt}(u)=0\\
\partial_{t}(v)+\partial_{x}(u)+v\cdot \partial_{x}(v)-\partial_{xxt}(v)=0
\end{cases}
$$

来源：[ Solitary wave simulations of the Boussinesq Systems ](https://arxiv.org/src/1605.04901v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}+v_{x}+(uv)_{x}-\frac{1}{6}u_{xxt}=0\\
v_{t}+u_{x}+vv_{x}-\frac{1}{6}v_{xxt}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF155 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(\frac{(v^{2})}{u})+u\cdot \partial_{x}(u+1-1)=0
\end{cases}
$$

来源：[ A novel energy-bounded Boussinesq model and a well balanced and stable numerical discretisation ](https://arxiv.org/src/2302.09924v1)

去除的系数：`H`, `b`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + v_x =0\\
v_t + (\frac{v^2}{u})_x + gu(u+b-H)_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF156 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)=\partial_{x}(\partial_{xx}(u+1))\\
\partial_{t}(v)+\partial_{x}(\frac{(v^{2})}{u})+u\cdot \partial_{x}(u+1-1)=\partial_{x}(v\cdot \partial_{xx}(u+1))+\partial_{xxt}(\frac{(v)}{u})+\partial_{xxx}(\frac{(v)}{u})
\end{cases}
$$

来源：[ A novel energy-bounded Boussinesq model and a well balanced and stable numerical discretisation ](https://arxiv.org/src/2302.09924v1)

去除的系数：`H`, `\alpha`, `\beta`, `\gamma`, `b`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x= (\alpha(u+b)_{xx})_x\\
v_t + (\frac{v^2}{u})_x + gu(u+b-H)_x =(\alpha v(u+b)_{xx})_x+ \beta (\frac{v}{u})_{xxt}+\gamma(\frac{v}{u})_{xxx}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF157 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)=\partial_{x}(\partial_{x}(u+1))\\
\partial_{t}(v)+\partial_{x}(\frac{(v^{2})}{u})+u\cdot \partial_{x}(u+1-1)=\partial_{x}(v\cdot \partial_{x}(u+1))+\partial_{x}(u\cdot \partial_{x}(v))
\end{cases}
$$

来源：[ A novel energy-bounded Boussinesq model and a well balanced and stable numerical discretisation ](https://arxiv.org/src/2302.09924v1)

去除的系数：`H`, `\epsilon`, `b`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+v_x=(\epsilon (u+b)_x)_x\\
v_t + (\frac{v^2}{u})_x + gu(u+b-H)_x =(v\epsilon (u+b)_x)_x+(\epsilon u v_x)_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF158 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)+v\cdot \partial_{z}(u)=0\\
\partial_{t}(v)+u\cdot \partial_{x}(v)+v\cdot \partial_{z}(v)=\partial_{x}(u)
\end{cases}
$$

来源：[ Ill-posedness of the hydrostatic Euler-Boussinesq equations and failure of hydrostatic limit ](https://arxiv.org/src/2403.17857v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u +u \partial_x u+ v \partial_z u=0\\
\partial_t v+u \partial_x v + v \partial_z v=\partial_x u
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF159 · 2变量 · boussinesq

$$
\begin{cases}
\partial_{tt}(u)-\partial_{xx}(u)=\partial_{x}(u)\cdot \partial_{xx}(u)+\partial_{ttxx}(u)-(u-v)\\
\partial_{tt}(v)-\partial_{xx}(v)=\partial_{x}(v)\cdot \partial_{xx}(v)+\partial_{ttxx}(v)+u-v
\end{cases}
$$

来源：[ Initial-value problem for coupled Boussinesq equations and a hierarchy of Ostrovsky equations ](https://arxiv.org/src/1104.3432v4)

去除的系数：`\alpha`, `\beta`, `\delta`, `\gamma`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_{tt} - u_{xx} = u_x u_{xx} + u_{ttxx} - \delta (u-v)\\
v_{tt} - c^2 v_{xx} = \alpha v_x v_{xx} + \beta v_{ttxx} + \gamma (u-v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF160 · 3变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+u\cdot \partial_{x}(u)+\partial_{x}(-v^{2}+w)\\
\partial_{t}(v)=\partial_{xxx}(v)-u\cdot \partial_{x}(v)\\
\partial_{t}(w)=\partial_{xxx}(w)-u\cdot \partial_{x}(w)
\end{cases}
$$

来源：[ Numerical calculation of N-periodic wave solutions to coupled KdV-type equations ](https://arxiv.org/src/1708.07258v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\frac{1}{4}u_{xxx}+3uu_x+3(-v^2+w)_x\\
v_t=-\frac{1}{2}v_{xxx}-3uv_x\\
w_t=\frac{1}{2}w_{xxx}-3uw_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF161 · 2变量 · wave

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(u)=0
\end{cases}
$$

来源：[ Kinetic layers and coupling conditions for macroscopic equations on networks I: the wave equation ](https://arxiv.org/src/1708.07757v1)

去除的系数：`a`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u + \partial_x v =0\\
\partial_t v + \partial_x (a^2 u ) =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF162 · 3变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxx}(u)+\partial_{x}(v\cdot u)-\partial_{x}(u)\cdot u^{2}=0\\
\partial_{t}(v)-\partial_{xxx}(v)-\partial_{x}(v)\cdot v+w\cdot \partial_{x}(w)+\partial_{x}(v)\cdot u^{2}-\partial_{x}(\partial_{x}(u)\cdot w)=0\\
\partial_{t}(w)+\partial_{xxx}(w)+\partial_{x}(w)\cdot v-\partial_{x}(w\cdot u^{2})+\partial_{xx}(v)\cdot u+\partial_{x}(v)\cdot \partial_{x}(u)=0
\end{cases}
$$

来源：[ Analytical and numerical solution of a coupled KdV-MKdV system ](https://arxiv.org/src/math-ph/0211018v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}+\frac{1}{2}u_{xxx}+\frac{3}{2}(vu)_{x}-\frac{3}{4}u_{x}u^{2}=0\\
v_{t}-\frac{1}{4}v_{xxx}-\frac{3}{2}v_{x}v+3ww_{x}+\frac{3}{4}v_{x}u^{2}- \frac{3}{2}(u_{x}w)_{x}=0\\
w_{t}+\frac{1}{2}w_{xxx}+\frac{3}{2}w_{x}v-\frac{3}{4}(wu^{2})_{x}+\frac{3}{4 }v_{xx}u+\frac{3}{2}v_{x}u_{x}=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF163 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)-u\cdot \partial_{x}(u)+\partial_{xxx}(u)+\partial_{x}(1)+\partial_{x}(u\cdot v)+\partial_{xxx}(1)=0\\
\partial_{t}(v)-v\cdot \partial_{x}(v)+\partial_{xxx}(v)-\partial_{x}(1)+\partial_{x}(v\cdot u)+\partial_{x}(1)+\partial_{xxx}(1)=0
\end{cases}
$$

来源：[ Nonsingular positon and complexiton solutions for the coupled KdV system ](https://arxiv.org/src/nlin/0509018v1)

去除的系数：`V_0v`, `\alpha`, `\beta`, `\epsilon_1`, `\epsilon_1vv`, `\epsilon_2`, `\epsilon_2uu`, `\epsilon_3u`, `\epsilon_3v`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}-6uu_x+u_{xxx}+\epsilon_1vv_x+\epsilon_2(uv)_x+\epsilon_3v_{xxx}=0\\
v_t-6\beta vv_x+\beta v_{xxx}-V_0v_x+\alpha[\epsilon_1(vu)_x+\epsilon_2uu_x+\epsilon_3u_{xxx}]=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF164 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+\frac{(1)}{\sqrt(t)}\cdot u\cdot \partial_{x}(u)\\
\partial_{t}(v)=\partial_{xxx}(v)+\frac{(1)}{\sqrt(t)}\cdot \partial_{x}(u\cdot v)
\end{cases}
$$

来源：[ Integrability of a Non-autonomous Coupled KdV System ](https://arxiv.org/src/nlin/0408001v2)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=u_{xxx}+ \frac{2}{\sqrt {t}} uu_x\\
v_t=v_{xxx}+ \frac{1}{\sqrt {t}} (uv)_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF165 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxx}(u)+\partial_{xxx}(v)+u\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)+\partial_{x}(u)\cdot v+v\cdot \partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{xxx}(u)+\partial_{xxx}(v)+u\cdot \partial_{x}(u)+u\cdot \partial_{x}(v)+\partial_{x}(u)\cdot v+v\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ Invariant Gibbs Measures and a.s. Global Well-Posedness for Coupled KdV Systems ](https://arxiv.org/src/0904.2816v1)

去除的系数：`a_{11}`, `a_{12}`, `a_{21}`, `a_{22}`, `b_1`, `b_2`, `b_3`, `b_4`, `b_5`, `b_6`, `b_7`, `b_8`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + a_{11} u_{xxx} + a_{12} v_{xxx} + b_1 u u_x + b_2 u v_x + b_3 u_x v + b_4 v v_x = 0\\
v_t + a_{21} u_{xxx} + a_{22} v_{xxx} + b_5 u u_x + b_6 u v_x + b_7 u_x v + b_8 v v_x = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF166 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{x}(\partial_{xx}(u)+u^{2})\\
\partial_{t}(v)=\partial_{x}(\partial_{xx}(v)+v^{2}+u^{2}-v\cdot u)
\end{cases}
$$

来源：[ Multi-component decompositions, linear superpositions, and new nonlinear integrable coupled KdV-type systems ](https://arxiv.org/src/2205.08186v1)

去除的系数：`a`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=(u_{xx}+au^2)_x\\
v_t=(v_{xx}+3v^2+\frac{2a^2}{3}u^2-2avu)_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF167 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxx}(u)+\partial_{x}(v)+v\cdot \partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{xxx}(v)+\partial_{x}(u)+\partial_{x}(v)+\partial_{x}(u\cdot v)=0
\end{cases}
$$

来源：[ Diophantine Conditions in Well-Posedness Theory of Coupled KdV-Type Systems: Local Theory ](https://arxiv.org/src/0904.2813v1)

去除的系数：`p`, `q`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + u_{xxx} + q v_x + v v_x = 0\\
v_t + v_{xxx} + q u_x + pv_x + (u v)_x = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF168 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxx}(u)+\partial_{xxx}(v)=0\\
\partial_{t}(v)+r\cdot \partial_{x}(v)+\partial_{xxx}(u)+\partial_{xxx}(v)=0
\end{cases}
$$

来源：[ Boundary Effects on the Controllability of Coupled KdV Systems ](https://arxiv.org/src/2302.13443v2)

去除的系数：`a`, `b`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + u_{xxx} + av_{xxx} =0\\
c v_t +rv_x +abu_{xxx} + v_{xxx} =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF169 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+u\cdot \partial_{x}(u)+\partial_{xxx}(u)+\partial_{xxx}(v)=0\\
\partial_{t}(v)+r\cdot \partial_{x}(v)+v\cdot \partial_{x}(v)+\partial_{xxx}(u)+\partial_{xxx}(v)=0
\end{cases}
$$

来源：[ Boundary Effects on the Controllability of Coupled KdV Systems ](https://arxiv.org/src/2302.13443v2)

去除的系数：`a`, `b`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + uu_x+u_{xxx} + av_{xxx} =0\\
c v_t +r v_x +vv_x+ab u_{xxx} +v_{xxx} =0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF170 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+u\cdot \partial_{x}(u)-v\cdot \partial_{x}(v)\\
\partial_{t}(v)=-\partial_{xxx}(v)-u\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ Non-local symmetries of the Hirota-Satsuma coupled KdV system and their applications ](https://arxiv.org/src/1301.0438v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=\frac{1}{2}u_{xxx}+3uu_x-6vv_x\\
v_t=-v_{xxx}-3uv_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF171 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxxx}(u)+\partial_{xxx}(u)+\partial_{xx}(u)+u\cdot \partial_{x}(u)=\partial_{x}(v)\\
\partial_{t}(v)-\partial_{xx}(v)+\partial_{x}(v)=\partial_{x}(u)
\end{cases}
$$

来源：[ Local null-controllability of a system coupling Kuramoto-Sivashinsky-KdV and elliptic equations ](https://arxiv.org/src/2208.12213v3)

去除的系数：`\Gamma`, `\gamma_1`, `\gamma_2`, `b`, `c`

<details><summary>对应原式与处理记录</summary>

```latex
u_t + \gamma_1 u_{xxxx} + u_{xxx} + \gamma_2 u_{xx} + u u_x = v_x\\
v_t -\Gamma v_{xx} + c v_x = b u_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF172 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{x}(u)+\partial_{xxx}(u)+u\cdot \partial_{x}(u)+\partial_{x}(u\cdot v)-v\cdot \partial_{x}(v)=0\\
\partial_{t}(v)-\partial_{x}(v)-\partial_{xxx}(v)-u\cdot \partial_{x}(u)+\partial_{x}(u\cdot v)+v\cdot \partial_{x}(v)=0
\end{cases}
$$

来源：[ Non-homogeneous boundary value problems for coupled KdV-KdV systems posed on the half line ](https://arxiv.org/src/2208.07053v3)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t+u_x+u_{xxx}+3uu_x+(uv)_x-vv_x=0\\
v_t-v_x-v_{xxx}-uu_x+(uv)_x+3vv_x=0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF173 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)+\partial_{xxx}(u)=u\cdot \partial_{x}(u)+v\cdot \partial_{x}(v)+\partial_{x}(u)\cdot v+u\cdot \partial_{x}(v)\\
\partial_{t}(v)+\partial_{xxx}(v)=u\cdot \partial_{x}(u)+v\cdot \partial_{x}(v)+\partial_{x}(u)\cdot v+u\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ Local Well-posedness of the Coupled KdV-KdV Systems on $\mathbb{R}$ ](https://arxiv.org/src/1812.08261v3)

去除的系数：`a_{1}`, `a_{2}`, `c_{11}`, `c_{12}`, `c_{21}`, `c_{22}`, `d_{11}`, `d_{12}`, `d_{21}`, `d_{22}`

<details><summary>对应原式与处理记录</summary>

```latex
u_t+a_{1}u_{xxx} = c_{11}uu_x+c_{12}vv_x+d_{11}u_{x}v+d_{12}uv_{x}\\
v_t+a_{2}v_{xxx}= c_{21}uu_x+c_{22}vv_x +d_{21}u_{x}v+d_{22}uv_{x}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF174 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{x}(u^{2}-\partial_{xx}(u)+v\cdot \partial_{x}(v))\\
\partial_{t}(v)=\partial_{xxx}(v)+u\cdot \partial_{x}(v)+\partial_{x}(u)\cdot v
\end{cases}
$$

来源：[ Extensions of dark KdV equations: nonhomogeneous classifications, bosonizations of fermionic systems and supersymmetric dark systems ](https://arxiv.org/src/2312.14538v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=(3u^2-u_{xx}+3vv_{x})_x\\
v_t=-4v_{xxx}+6uv_x+3u_xv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF175 · 2变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+u\cdot \partial_{x}(u)+v\cdot \partial_{x}(v)\\
\partial_{t}(v)=\partial_{xxx}(v)+\partial_{x}(u\cdot v)+v\cdot \partial_{x}(v)
\end{cases}
$$

来源：[ The Method of ${\cal M}_{n}$-Extension: The KdV Equation ](https://arxiv.org/src/2501.04673v1)

去除的系数：`\alpha`, `\beta`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=u_{xxx}+6 u u_{x}+6 \alpha v v_{x}\\
v_{t}=v_{xxx}+6 (uv)_{x}+6 \beta v v_{x}
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF176 · 3变量 · dispersive

$$
\begin{cases}
\partial_{t}(u)=\partial_{xxx}(u)+u\cdot \partial_{x}(u)+v\cdot \partial_{x}(v)+\partial_{x}(w\cdot v)\\
\partial_{t}(v)=\partial_{xxx}(v)+\partial_{x}(u\cdot v)+v\cdot \partial_{x}(v)+\partial_{x}(v\cdot w)+w\cdot \partial_{x}(w)\\
\partial_{t}(w)=\partial_{xxx}(w)+\partial_{x}(u\cdot w)+v\cdot \partial_{x}(v)+\partial_{x}(v\cdot w)-w\cdot \partial_{x}(w)
\end{cases}
$$

来源：[ The Method of ${\cal M}_{n}$-Extension: The KdV Equation ](https://arxiv.org/src/2501.04673v1)

去除的系数：无符号系数

<details><summary>对应原式与处理记录</summary>

```latex
u_t=u_{xxx}+6uu_x+6vv_x+6(wv)_x\\
v_t=v_{xxx}+6(uv)_x+12vv_x+6(vw)_x+12ww_x\\
w_t=w_{xxx}+6(uw)_x+6vv_x+6(vw)_x-6ww_x
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF177 · 2变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(1)-\partial_{x}(1)+u\cdot (r-u-v)\\
\partial_{t}(v)=\partial_{xx}(1)-\partial_{x}(1)+1-v-u\cdot v
\end{cases}
$$

来源：[ Effect of protection zone on the dynamics of a diffusion-advection population-toxicant model ](https://arxiv.org/src/2508.01246v1)

去除的系数：`a_1u`, `a_2v`, `d_1u`, `d_2v`, `h`, `m`, `p`, `q`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=d_1u_{xx}-a_1u_x+u( r-u-mv )\\
v_t=d_2v_{xx}-a_2v_x+h-qv-puv
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF178 · 2变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+u\cdot (1+v-u)\\
\partial_{t}(v)=\Delta(v)+v\cdot (1-v-u)
\end{cases}
$$

来源：[ Spreading properties of a three-component reaction-diffusion model for the population of farmers and hunter-gatherers ](https://arxiv.org/src/1812.04440v2)

去除的系数：`b`, `d`, `g`, `s`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_tu=\Delta u+u(1+sv-u)\\
\partial_tv=d\Delta v+bv(1-v-gu)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF179 · 2变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u\cdot (1-u-v)\\
\partial_{t}(v)=\partial_{xx}(1)+v\cdot (1-v-u)
\end{cases}
$$

来源：[ The long-time behavior of solutions of a three-component reaction-diffusion model for the population dynamics of farmers and hunter-gatherers: the different motility case ](https://arxiv.org/src/2404.00907v1)

去除的系数：`a`, `d_cv`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=u_{xx}+au(1-u-v)\\
v_t=d_cv_{xx}+v(1-v-u)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF180 · 2变量 · population_competition

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+\nabla\cdot(v^{2}\cdot \nabla(\frac{(u)}{v}))+u\cdot (1-u+v)\\
\partial_{t}(v)=\Delta(v)+\nabla\cdot(u^{2}\cdot \nabla(\frac{(v)}{u}))+v\cdot (1+u-v)
\end{cases}
$$

来源：[ Large time behavior of solutions to a cooperative model with population flux by attractive transition ](https://arxiv.org/src/2504.04166v1)

去除的系数：`\alpha`, `\beta`, `a_{1}`, `a_{2}`, `b_{1}`, `b_{2}`, `c_{1}`, `c_{2}`, `d_{1}`, `d_{2}`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}=d_{1}\Delta u+\alpha\nabla\cdot[ v^{2}\nabla(\dfrac{u}{v})] +u(a_{1}-b_{1}u+c_{1}v)\\
v_{t}=d_{2}\Delta v +\beta\nabla\cdot[ u^{2}\nabla(\dfrac{v}{u})] +v(a_{2}+b_{2}u-c_{2}v)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF181 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=u\cdot v-u+\partial_{xx}(u)\\
\partial_{t}(v)=u\cdot v+\partial_{xx}(v)
\end{cases}
$$

来源：[ Recurrent host mobility in spatial epidemics: beyond reaction-diffusion ](https://arxiv.org/src/1106.3461v1)

去除的系数：`D`, `\alpha`, `\beta`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_{t}u = \alpha uv-\beta u+D\partial_{x}^{2}u\\
\partial_{t}v = -\alpha uv+D\partial_{x}^{2}v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF182 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=-\frac{(u\cdot v)}{u+v}+v\\
\partial_{t}(v)-\Delta(v)=\frac{(u\cdot v)}{u+v}-v
\end{cases}
$$

来源：[ Spatial diffusion and periodic evolving of domain in an SIS epidemic model ](https://arxiv.org/src/2011.07550v1)

去除的系数：`\beta (x)`, `\gamma(x)`, `d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
u_{t}-d_u\Delta u=-\frac{\beta (x) uv}{u+v}+\gamma(x)v\\
v_{t}-d_v\Delta v=\frac{\beta (x) uv}{u+v}-\gamma(x)v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF183 · 3变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=1-w\cdot u-u+w+1\\
\partial_{t}(v)-\Delta(v)=w\cdot u-v-1-v\\
\partial_{t}(w)-\Delta(w)=w\cdot u+v-1-w
\end{cases}
$$

来源：[ Diffusion-Reaction Epidemic Model with a Free Boundary ](https://arxiv.org/src/2511.07291v1)

去除的系数：`A`, `\alpha`, `\beta_1`, `\mu_1`, `\mu_2`, `\mu_3`, `d_1`, `d_2`, `d_3`, `p`, `r_1v`, `r_2`, `r_2w`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-d_1\Delta u=A-\alpha wu-\mu_1 u+r_2 w+r_1v\\
v_t-d_2\Delta v=(1-p)\alpha wu-\beta_1 v-r_1v-\mu_2 v\\
w_t-d_3\Delta w=p\alpha wu+\beta_1 v-r_2w-\mu_3 w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF184 · 3变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=1-w\cdot u-u+w+1\\
\partial_{t}(v)-\Delta(v)=w\cdot u-v\\
\partial_{t}(w)-\Delta(w)=w\cdot u+v-w
\end{cases}
$$

来源：[ Diffusion-Reaction Epidemic Model with a Free Boundary ](https://arxiv.org/src/2511.07291v1)

去除的系数：`A`, `\alpha`, `\beta_1`, `\mu_1`, `\mu_2`, `\mu_3`, `d_1`, `d_2`, `d_3`, `p`, `r_1`, `r_1v`, `r_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-d_1\Delta u=A-\alpha wu-\mu_1 u+r_2 w+r_1v\\
v_t-d_2\Delta v=(1-p)\alpha wu-(\beta_1 +r_1+\mu_2) v\\
w_t-d_3\Delta w=p\alpha wu+\beta_1 v-(r_2+\mu_3) w
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF185 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-u\cdot v\\
\partial_{t}(v)=\Delta(v)+u\cdot v-v
\end{cases}
$$

来源：[ On the well-posedness of a nonlinear diffusive SIR epidemic model ](https://arxiv.org/src/2109.09039v1)

去除的系数：`D_u`, `D_v`, `\beta`, `\mu`

<details><summary>对应原式与处理记录</summary>

```latex
u_t = D_u \Delta u -\beta uv\\
v_t = D_v \Delta v + \beta uv -\mu v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF186 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)+u\cdot v-\partial_{xx}(u)=0\\
\partial_{t}(v)-u\cdot v-\partial_{xx}(v)-v=0
\end{cases}
$$

来源：[ On the well-posedness of a nonlinear diffusive SIR epidemic model ](https://arxiv.org/src/2109.09039v1)

去除的系数：`\mu`

<details><summary>对应原式与处理记录</summary>

```latex
u_t +uv - u_{xx} = 0\\
v_t - uv-v_{xx} - \mu v = 0
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF187 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=u\cdot v+v\\
\partial_{t}(v)=\Delta(v)+u\cdot v-v
\end{cases}
$$

来源：[ On degenerate reaction-diffusion epidemic models with mass action or standard incidence mechanism ](https://arxiv.org/src/2311.06434v3)

去除的系数：`\beta(x)`, `\gamma(x)`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=-\beta(x) u v+\gamma(x) v\\
\partial_t v=d_v\Delta v+\beta(x) u v-\gamma(x) v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF188 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-u\cdot v+v\\
\partial_{t}(v)=u\cdot v-v
\end{cases}
$$

来源：[ On degenerate reaction-diffusion epidemic models with mass action or standard incidence mechanism ](https://arxiv.org/src/2311.06434v3)

去除的系数：`\beta(x)`, `\gamma(x)`, `d_u`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=d_u\Delta u-\beta(x) u v+\gamma(x) v\\
\partial_t v=\beta(x) u v-\gamma(x) v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF189 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\frac{(u\cdot v)}{u+v}+v\\
\partial_{t}(v)=\Delta(v)+\frac{(u\cdot v)}{u+v}-v
\end{cases}
$$

来源：[ On degenerate reaction-diffusion epidemic models with mass action or standard incidence mechanism ](https://arxiv.org/src/2311.06434v3)

去除的系数：`\beta(x)`, `\gamma(x)`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=-\beta(x) \frac{u v}{u+v}+\gamma(x) v\\
\partial_t v=d_v\Delta v+\beta(x) \frac{u v}{u+v}-\gamma(x) v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF190 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)-\frac{(u\cdot v)}{u+v}+v\\
\partial_{t}(v)=\frac{(u\cdot v)}{u+v}-v
\end{cases}
$$

来源：[ On degenerate reaction-diffusion epidemic models with mass action or standard incidence mechanism ](https://arxiv.org/src/2311.06434v3)

去除的系数：`\beta(x)`, `\gamma(x)`, `d_u`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u=d_u\Delta u-\beta(x) \frac{u v}{u+v}+\gamma(x) v\\
\partial_t v=\beta(x) \frac{u v}{u+v}-\gamma(x) v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF191 · 4变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+1-u\cdot v-u\cdot \frac{(p)}{p+1}-u+w\\
\partial_{t}(v)=\partial_{xx}(v)+u\cdot v+u\cdot \frac{(p)}{p+1}-v\\
\partial_{t}(w)=\partial_{xx}(w)+v-w\\
\partial_{t}(p)=\partial_{xx}(p)-\partial_{x}(p)+v+p\cdot (1-p)-p
\end{cases}
$$

来源：[ Global stability and uniform persistence of the reaction-convection-diffusion cholera epidemic model ](https://arxiv.org/src/1701.01407v1)

去除的系数：`D_{1}`, `D_{2}`, `D_{3}`, `D_{4}`, `K`, `K_{p}`, `U`, `\beta_{1}`, `\beta_{2}`, `\delta`, `\gamma`, `\sigma`, `\xi`, `b`, `d`, `g`

<details><summary>对应原式与处理记录</summary>

```latex
\frac{\partial u}{\partial t} = D_{1} \frac{\partial^{2} u}{\partial x^{2}} +b - \beta_{1}uv - \beta_{2}u\frac{p}{p+K} -d u+\sigma w\\
\frac{\partial v}{\partial t} = D_{2} \frac{\partial^{2} v}{\partial x^{2}} + \beta_{1}uv + \beta_{2}u\frac{p}{p+K} - v(d + \gamma)\\
\frac{\partial w}{\partial t} = D_{3} \frac{\partial^{2} w}{\partial x^{2}} + \gamma v- w(d + \sigma)\\
\frac{\partial p}{\partial t} = D_{4} \frac{\partial^{2} p}{\partial x^{2}} - U\frac{\partial p}{\partial x} + \xi v + gp(1-\frac{p}{K_{p}})-\delta p
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF192 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+1-u+v\\
\partial_{t}(v)=\partial_{xx}(v)-v
\end{cases}
$$

来源：[ Global stability and uniform persistence of the reaction-convection-diffusion cholera epidemic model ](https://arxiv.org/src/1701.01407v1)

去除的系数：`D`, `\sigma`, `b`, `d`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_{t}u = D \partial_{xx}^{2}u + b - du + \sigma v\\
\partial_{t}v = D \partial_{xx}^{2}v - v (d+\sigma)
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF193 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=u\cdot v+v\\
\partial_{t}(v)-\Delta(v)=u\cdot v-v
\end{cases}
$$

来源：[ On a diffusive SIS epidemic model with mass action mechanism and birth-death effect: Analysis, simulations and comparison with other mechanisms ](https://arxiv.org/src/1807.03451v1)

去除的系数：`\beta(x)`, `\gamma(x)`, `d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
u_t - d_u \Delta u = -\beta(x) uv +\gamma(x) v\\
v_t - d_v \Delta v = \beta(x) uv -\gamma(x) v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF194 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=1-u-u\cdot v+v\\
\partial_{t}(v)-\Delta(v)=u\cdot v-v
\end{cases}
$$

来源：[ On a diffusive SIS epidemic model with mass action mechanism and birth-death effect: Analysis, simulations and comparison with other mechanisms ](https://arxiv.org/src/1807.03451v1)

去除的系数：`\Lambda(x)`, `\beta(x)`, `\gamma(x)`, `\mu (x)`, `d_u`, `d_v`

<details><summary>对应原式与处理记录</summary>

```latex
u_t-d_u\Delta u=\Lambda(x)-u-\beta(x)uv+\gamma(x)v\\
v_t-d_v\Delta v=\beta(x)uv-[\gamma(x)+\mu (x)] v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF195 · 2变量 · epidemic

$$
\begin{cases}
\partial_{t}(u)=\partial_{xx}(u)+u\cdot (1-(u+v))-x\cdot u+x\cdot v\\
\partial_{t}(v)=\partial_{xx}(v)+v\cdot (r-(u+v))+x\cdot u-x\cdot v
\end{cases}
$$

来源：[ Front propagation in hybrid reaction-diffusion epidemic models with spatial heterogeneity. Part II: Pulsating traveling waves ](https://arxiv.org/src/2607.11869v1)

去除的系数：`\kappa`, `\mu_1`, `\mu_2`

<details><summary>对应原式与处理记录</summary>

```latex
\partial_t u =\partial_{xx}u + u(1-\kappa(u+v)) - \mu_1(x)u +\mu_2(x) v\\
\partial_t v =\partial_{xx}v + v(r-\kappa(u +v)) + \mu_1(x)u -\mu_2(x) v
```

无未展开函数；直接对原式中的标量系数表达式规范化。
</details>

## CF196 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+\partial_{x}(u)+\frac{(u^{2})}{v}-u+1\\
\partial_{t}(v)=\Delta(v)+\partial_{x}(v)+u^{2}-v
\end{cases}
$$

来源：[ Turing Patterns in two dimensional reaction-diffusion system: effect of an electric field ](https://arxiv.org/src/0812.4623v1)

去除的系数：`D`, `E`, `\mu`, `\sigma`, `z_1`, `z_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=D\Delta u+z_2 E D u_x+\frac{u^2}{v}-u+\sigma\\
v_t=\Delta v+z_1 E v_x+\mu (u^2-v)
```

Paper explicitly gives both reaction pairs immediately following general A/B evolution equations; only these source-defined choices are instantiated
</details>

## CF197 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)=\Delta(u)+\partial_{x}(u)+v-\frac{(u\cdot v)}{1+v^{2}}\\
\partial_{t}(v)=\Delta(v)+\partial_{x}(v)+1-v-\frac{(u\cdot v)}{1+v^{2}}
\end{cases}
$$

来源：[ Turing Patterns in two dimensional reaction-diffusion system: effect of an electric field ](https://arxiv.org/src/0812.4623v1)

去除的系数：`D`, `E`, `\sigma`, `a`, `b`, `z_1`, `z_2`

<details><summary>对应原式与处理记录</summary>

```latex
u_t=D\Delta u+z_2 E D u_x+\sigma b (v-\frac{u v}{1+v^2})\\
v_t=\Delta v+z_1 E v_x+a-v-\frac{4u v}{1+v^2}
```

Paper explicitly gives both reaction pairs immediately following general A/B evolution equations; only these source-defined choices are instantiated
</details>

## CF198 · 3变量 · thermoelasticity

$$
\begin{cases}
\partial_{tt}(u)-\partial_{xx}(u)+\partial_{x}(v)=0\\
\partial_{t}(v)+\partial_{x}(w)+\partial_{xt}(u)=0\\
\partial_{t}(w)+w+\partial_{x}(v)=0
\end{cases}
$$

来源：[ Remarks on Exponential Stability for a Coupled System of Elasticity and Thermoelasticity with Second Sound ](https://arxiv.org/src/2009.08239v1)

去除的系数：`\tau`, `a`, `k`, `m`

<details><summary>对应原式与处理记录</summary>

```latex
u_{tt} - a u_{xx} + m v_x = 0\\
v_t + k w_x + mu_{xt} = 0\\
\tau w_t + w + kv_x = 0
```

Retain the complete connected thermoelastic subsystem; the remaining independent wave equation has no variables in common and supplies no forcing or closure
</details>

## CF199 · 2变量 · thermoelasticity

$$
\begin{cases}
\partial_{tt}(u)-\partial_{xx}(u)+\partial_{x}(v)=0\\
\partial_{t}(v)-\partial_{xx}(v)+\partial_{xt}(u)=0
\end{cases}
$$

来源：[ Remarks on Exponential Stability for a Coupled System of Elasticity and Thermoelasticity with Second Sound ](https://arxiv.org/src/2009.08239v1)

去除的系数：`a`, `k`, `m`

<details><summary>对应原式与处理记录</summary>

```latex
u_{tt} - a u_{xx} + m v_x = 0\\
v_t - k^2 v_{xx} + mu_{xt} = 0
```

Retain the complete connected thermoelastic subsystem; the remaining independent wave equation has no variables in common and supplies no forcing or closure
</details>

## CF200 · 2变量 · reaction_diffusion

$$
\begin{cases}
\partial_{t}(u)-\Delta(u)=u\cdot (1-v)\\
\partial_{t}(v)=(1-v)\cdot u
\end{cases}
$$

来源：[ Efficient bound preserving and asymptotic preserving semi-implicit schemes for the fast reaction-diffusion system ](https://arxiv.org/src/2404.18463v1)

去除的系数：`\delta`, `\epsilon`, `\lambda`, `d_1`

<details><summary>对应原式与处理记录</summary>

```latex
\delta \partial_t u - d_1 \Delta u = -\frac{1}{\epsilon} u \lambda (1 - v)\\
\delta \partial_t v = \frac{1}{\epsilon}(1 - v) u
```

u_epsilon/v_epsilon are the same two source dependent fields indexed by the reaction parameter; drop the family index consistently, then normalize scalar epsilon/delta/lambda coefficients
</details>
