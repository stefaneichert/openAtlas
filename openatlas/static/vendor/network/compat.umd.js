!function(n,t){"object"==typeof exports&&"undefined"!=typeof module?t(exports,require("preact/hooks"),require("preact")):"function"==typeof define&&define.amd?define(["exports","preact/hooks","preact"],t):t(n.preactCompat={},n.preactHooks,n.preact)}(this,function(n,t,e){function r(n,t){for(var e in t)n[e]=t[e];return n}function u(n,t){for(var e in n)if("__source"!==e&&!(e in t))return!0;for(var r in t)if("__source"!==r&&n[r]!==t[r])return!0;return!1}var i=function(n){var t,e;function r(t){var e;return(e=n.call(this,t)||this).isPureReactComponent=!0,e}return e=n,(t=r).prototype=Object.create(e.prototype),t.prototype.constructor=t,t.__proto__=e,r.prototype.shouldComponentUpdate=function(n,t){return u(this.props,n)||u(this.state,t)},r}(e.Component);function o(n,t){function i(n){var e=this.props.ref,r=e==n.ref;return!r&&e&&(e.call?e(null):e.current=null),t?!t(this.props,n)||!r:u(this.props,n)}function o(t){return this.shouldComponentUpdate=i,e.createElement(n,r({},t))}return o.prototype.isReactComponent=!0,o.displayName="Memo("+(n.displayName||n.name)+")",o.t=!0,o}var f=e.options.vnode;function c(n){function t(t){var e=r({},t);return delete e.ref,n(e,t.ref)}return t.prototype.isReactComponent=!0,t.t=!0,t.displayName="ForwardRef("+(n.displayName||n.name)+")",t}e.options.vnode=function(n){n.type&&n.type.t&&n.ref&&(n.props.ref=n.ref,n.ref=null),f&&f(n)};var l=function(n,t){return n?e.toChildArray(n).map(t):null},a={map:l,forEach:l,count:function(n){return n?e.toChildArray(n).length:0},only:function(n){if(1!==(n=e.toChildArray(n)).length)throw new Error("Children.only() expects only one child.");return n[0]},toArray:e.toChildArray},s=e.options.__e;function h(n){return n&&((n=r({},n)).__c=null,n.__k=n.__k&&n.__k.map(h)),n}function v(n){this.__u=0,this.__b=null}function d(n){var t=n.__.__c;return t&&t.u&&t.u(n)}function p(n){var t,r,u;function i(i){if(t||(t=n()).then(function(n){r=n.default||n},function(n){u=n}),u)throw u;if(!r)throw t;return e.createElement(r,i)}return i.displayName="Lazy",i.t=!0,i}function m(){this.i=null,this.o=null}e.options.__e=function(n,t,e){if(n.then)for(var r,u=t;u=u.__;)if((r=u.__c)&&r.l)return r.l(n,t.__c);s(n,t,e)},(v.prototype=new e.Component).l=function(n,t){var e=this,r=d(e.__v),u=!1,i=function(){u||(u=!0,r?r(o):o())};t.__c=t.componentWillUnmount,t.componentWillUnmount=function(){i(),t.__c&&t.__c()};var o=function(){--e.__u||(e.__v.__k[0]=e.state.u,e.setState({u:e.__b=null}))};e.__u++||e.setState({u:e.__b=e.__v.__k[0]}),n.then(i,i)},v.prototype.render=function(n,t){return this.__b&&(this.__v.__k[0]=h(this.__b),this.__b=null),[e.createElement(e.Component,null,t.u?null:n.children),t.u&&n.fallback]};var y=function(n,t,e){if(++e[1]===e[0]&&n.o.delete(t),n.props.revealOrder&&("t"!==n.props.revealOrder[0]||!n.o.size))for(e=n.i;e;){for(;e.length>3;)e.pop()();if(e[1]<e[0])break;n.i=e=e[2]}};(m.prototype=new e.Component).u=function(n){var t=this,e=d(t.__v),r=t.o.get(n);return r[0]++,function(u){var i=function(){t.props.revealOrder?(r.push(u),y(t,n,r)):u()};e?e(i):i()}},m.prototype.render=function(n){this.i=null,this.o=new Map;var t=e.toChildArray(n.children);n.revealOrder&&"b"===n.revealOrder[0]&&t.reverse();for(var r=t.length;r--;)this.o.set(t[r],this.i=[1,0,this.i]);return n.children},m.prototype.componentDidUpdate=m.prototype.componentDidMount=function(){var n=this;n.o.forEach(function(t,e){y(n,e,t)})};var b=function(){function n(){}var t=n.prototype;return t.getChildContext=function(){return this.props.context},t.render=function(n){return n.children},n}();function g(n){var t=this,r=n.container,u=e.createElement(b,{context:t.context},n.vnode);return t.s&&t.s!==r&&(t.h.parentNode&&t.s.removeChild(t.h),e._e(t.v),t.p=!1),n.vnode?t.p?(r.__k=t.__k,e.render(u,r),t.__k=r.__k):(t.h=document.createTextNode(""),e.hydrate("",r),r.appendChild(t.h),t.p=!0,t.s=r,e.render(u,r,t.h),t.__k=this.h.__k):t.p&&(t.h.parentNode&&t.s.removeChild(t.h),e._e(t.v)),t.v=u,t.componentWillUnmount=function(){t.h.parentNode&&t.s.removeChild(t.h),e._e(t.v)},null}function w(n,t){return e.createElement(g,{vnode:n,container:t})}var x=/^(?:accent|alignment|arabic|baseline|cap|clip|color|fill|flood|font|glyph|horiz|marker|overline|paint|stop|strikethrough|stroke|text|underline|unicode|units|v|vector|vert|word|writing|x)[A-Z]/;e.Component.prototype.isReactComponent={};var E="undefined"!=typeof Symbol&&Symbol.for&&Symbol.for("react.element")||60103;function _(n,t,e){if(null==t.__k)for(;t.firstChild;)t.removeChild(t.firstChild);return A(n,t,e)}function A(n,t,r){return e.render(n,t),"function"==typeof r&&r(),n?n.__c:null}var S=e.options.event;function k(n,t){n["UNSAFE_"+t]&&!n[t]&&Object.defineProperty(n,t,{configurable:!1,get:function(){return this["UNSAFE_"+t]},set:function(n){this["UNSAFE_"+t]=n}})}e.options.event=function(n){return S&&(n=S(n)),n.persist=function(){},n.nativeEvent=n};var C={configurable:!0,get:function(){return this.class}},N=e.options.vnode;function F(n){return e.createElement.bind(null,n)}function R(n){return!!n&&n.$$typeof===E}function j(n){return R(n)?e.cloneElement.apply(null,arguments):n}function M(n){return!!n.__k&&(e.render(null,n),!0)}function O(n){return n&&(n.base||1===n.nodeType&&n)||null}e.options.vnode=function(n){n.$$typeof=E;var t=n.type,r=n.props;if("function"!=typeof t){var u,i,o;for(o in r.defaultValue&&(r.value||0===r.value||(r.value=r.defaultValue),delete r.defaultValue),Array.isArray(r.value)&&r.multiple&&"select"===t&&(e.toChildArray(r.children).forEach(function(n){-1!=r.value.indexOf(n.props.value)&&(n.props.selected=!0)}),delete r.value),r)if(u=x.test(o))break;if(u)for(o in i=n.props={},r)i[x.test(o)?o.replace(/([A-Z0-9])/,"-$1").toLowerCase():o]=r[o]}(r.class||r.className)&&(C.enumerable="className"in r,r.className&&(r.class=r.className),Object.defineProperty(r,"className",C)),function(t){var e=n.type,r=n.props;if(r&&"string"==typeof e){var u={};for(var i in r)/^on(Ani|Tra|Tou)/.test(i)&&(r[i.toLowerCase()]=r[i],delete r[i]),u[i.toLowerCase()]=i;if(u.ondoubleclick&&(r.ondblclick=r[u.ondoubleclick],delete r[u.ondoubleclick]),u.onbeforeinput&&(r.onbeforeinput=r[u.onbeforeinput],delete r[u.onbeforeinput]),u.onchange&&("textarea"===e||"input"===e.toLowerCase()&&!/^fil|che|ra/i.test(r.type))){var o=u.oninput||"oninput";r[o]||(r[o]=r[u.onchange],delete r[u.onchange])}}}(),"function"==typeof t&&!t.m&&t.prototype&&(k(t.prototype,"componentWillMount"),k(t.prototype,"componentWillReceiveProps"),k(t.prototype,"componentWillUpdate"),t.m=!0),N&&N(n)};var U=function(n,t){return n(t)},z={useState:t.useState,useReducer:t.useReducer,useEffect:t.useEffect,useLayoutEffect:t.useLayoutEffect,useRef:t.useRef,useImperativeHandle:t.useImperativeHandle,useMemo:t.useMemo,useCallback:t.useCallback,useContext:t.useContext,useDebugValue:t.useDebugValue,version:"16.8.0",Children:a,render:_,hydrate:_,unmountComponentAtNode:M,createPortal:w,createElement:e.createElement,createContext:e.createContext,createFactory:F,cloneElement:j,createRef:e.createRef,Fragment:e.Fragment,isValidElement:R,findDOMNode:O,Component:e.Component,PureComponent:i,memo:o,forwardRef:c,unstable_batchedUpdates:U,Suspense:v,SuspenseList:m,lazy:p};Object.keys(t).forEach(function(e){n[e]=t[e]}),n.createElement=e.createElement,n.createContext=e.createContext,n.createRef=e.createRef,n.Fragment=e.Fragment,n.Component=e.Component,n.version="16.8.0",n.Children=a,n.render=_,n.hydrate=A,n.unmountComponentAtNode=M,n.createPortal=w,n.createFactory=F,n.cloneElement=j,n.isValidElement=R,n.findDOMNode=O,n.PureComponent=i,n.memo=o,n.forwardRef=c,n.unstable_batchedUpdates=U,n.Suspense=v,n.SuspenseList=m,n.lazy=p,n.default=z});
//# sourceMappingURL=compat.umd.js.map