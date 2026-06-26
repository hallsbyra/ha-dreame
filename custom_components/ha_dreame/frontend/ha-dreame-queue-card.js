const Ee="modulepreload",Ce=function(r){return"/"+r},Y={},Re=function(e,t,i){let n=Promise.resolve();if(t&&t.length>0){let a=function(u){return Promise.all(u.map(h=>Promise.resolve(h).then(c=>({status:"fulfilled",value:c}),c=>({status:"rejected",reason:c}))))};document.getElementsByTagName("link");const o=document.querySelector("meta[property=csp-nonce]"),l=o?.nonce||o?.getAttribute("nonce");n=a(t.map(u=>{if(u=Ce(u),u in Y)return;Y[u]=!0;const h=u.endsWith(".css"),c=h?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${u}"]${c}`))return;const m=document.createElement("link");if(m.rel=h?"stylesheet":Ee,h||(m.as="script"),m.crossOrigin="",m.href=u,l&&m.setAttribute("nonce",l),document.head.appendChild(m),h)return new Promise((f,y)=>{m.addEventListener("load",f),m.addEventListener("error",()=>y(new Error(`Unable to preload CSS for ${u}`)))})}))}function s(o){const l=new Event("vite:preloadError",{cancelable:!0});if(l.payload=o,window.dispatchEvent(l),!l.defaultPrevented)throw o}return n.then(o=>{for(const l of o||[])l.status==="rejected"&&s(l.reason);return e().catch(s)})};const L=globalThis,K=L.ShadowRoot&&(L.ShadyCSS===void 0||L.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),X=new WeakMap;let pe=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(K&&e===void 0){const i=t!==void 0&&t.length===1;i&&(e=X.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&X.set(t,e))}return e}toString(){return this.cssText}};const Ie=r=>new pe(typeof r=="string"?r:r+"",void 0,Z),Pe=(r,...e)=>{const t=r.length===1?r[0]:e.reduce((i,n,s)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+r[s+1],r[0]);return new pe(t,r,Z)},Oe=(r,e)=>{if(K)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const i=document.createElement("style"),n=L.litNonce;n!==void 0&&i.setAttribute("nonce",n),i.textContent=t.cssText,r.appendChild(i)}},ee=K?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return Ie(t)})(r):r;const{is:Me,defineProperty:ke,getOwnPropertyDescriptor:Ne,getOwnPropertyNames:Te,getOwnPropertySymbols:Ue,getPrototypeOf:Le}=Object,v=globalThis,te=v.trustedTypes,qe=te?te.emptyScript:"",He=v.reactiveElementPolyfillSupport,C=(r,e)=>r,W={toAttribute(r,e){switch(e){case Boolean:r=r?qe:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},me=(r,e)=>!Me(r,e),re={attribute:!0,type:String,converter:W,reflect:!1,useDefault:!1,hasChanged:me};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),v.litPropertyMetadata??(v.litPropertyMetadata=new WeakMap);let A=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=re){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),n=this.getPropertyDescriptor(e,i,t);n!==void 0&&ke(this.prototype,e,n)}}static getPropertyDescriptor(e,t,i){const{get:n,set:s}=Ne(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:n,set(o){const l=n?.call(this);s?.call(this,o),this.requestUpdate(e,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??re}static _$Ei(){if(this.hasOwnProperty(C("elementProperties")))return;const e=Le(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(C("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(C("properties"))){const t=this.properties,i=[...Te(t),...Ue(t)];for(const n of i)this.createProperty(n,t[n])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[i,n]of t)this.elementProperties.set(i,n)}this._$Eh=new Map;for(const[t,i]of this.elementProperties){const n=this._$Eu(t,i);n!==void 0&&this._$Eh.set(n,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const n of i)t.unshift(ee(n))}else e!==void 0&&t.push(ee(e));return t}static _$Eu(e,t){const i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Oe(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),n=this.constructor._$Eu(e,i);if(n!==void 0&&i.reflect===!0){const s=(i.converter?.toAttribute!==void 0?i.converter:W).toAttribute(t,i.type);this._$Em=e,s==null?this.removeAttribute(n):this.setAttribute(n,s),this._$Em=null}}_$AK(e,t){const i=this.constructor,n=i._$Eh.get(e);if(n!==void 0&&this._$Em!==n){const s=i.getPropertyOptions(n),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:W;this._$Em=n;const l=o.fromAttribute(t,s.type);this[n]=l??this._$Ej?.get(n)??l,this._$Em=null}}requestUpdate(e,t,i,n=!1,s){if(e!==void 0){const o=this.constructor;if(n===!1&&(s=this[e]),i??(i=o.getPropertyOptions(e)),!((i.hasChanged??me)(s,t)||i.useDefault&&i.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:n,wrapped:s},o){i&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),n===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[n,s]of this._$Ep)this[n]=s;this._$Ep=void 0}const i=this.constructor.elementProperties;if(i.size>0)for(const[n,s]of i){const{wrapped:o}=s,l=this[n];o!==!0||this._$AL.has(n)||l===void 0||this.C(n,void 0,s,l)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[C("elementProperties")]=new Map,A[C("finalized")]=new Map,He?.({ReactiveElement:A}),(v.reactiveElementVersions??(v.reactiveElementVersions=[])).push("2.1.2");const R=globalThis,ie=r=>r,q=R.trustedTypes,ne=q?q.createPolicy("lit-html",{createHTML:r=>r}):void 0,fe="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,_e="?"+_,De=`<${_e}>`,b=document,O=()=>b.createComment(""),M=r=>r===null||typeof r!="object"&&typeof r!="function",J=Array.isArray,ze=r=>J(r)||typeof r?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,se=/-->/g,oe=/>/g,g=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ae=/'/g,le=/"/g,ve=/^(?:script|style|textarea|title)$/i,je=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),p=je(1),x=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),ce=new WeakMap,$=b.createTreeWalker(b,129);function ge(r,e){if(!J(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return ne!==void 0?ne.createHTML(e):e}const Be=(r,e)=>{const t=r.length-1,i=[];let n,s=e===2?"<svg>":e===3?"<math>":"",o=E;for(let l=0;l<t;l++){const a=r[l];let u,h,c=-1,m=0;for(;m<a.length&&(o.lastIndex=m,h=o.exec(a),h!==null);)m=o.lastIndex,o===E?h[1]==="!--"?o=se:h[1]!==void 0?o=oe:h[2]!==void 0?(ve.test(h[2])&&(n=RegExp("</"+h[2],"g")),o=g):h[3]!==void 0&&(o=g):o===g?h[0]===">"?(o=n??E,c=-1):h[1]===void 0?c=-2:(c=o.lastIndex-h[2].length,u=h[1],o=h[3]===void 0?g:h[3]==='"'?le:ae):o===le||o===ae?o=g:o===se||o===oe?o=E:(o=g,n=void 0);const f=o===g&&r[l+1].startsWith("/>")?" ":"";s+=o===E?a+De:c>=0?(i.push(u),a.slice(0,c)+fe+a.slice(c)+_+f):a+_+(c===-2?l:f)}return[ge(r,s+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]};class k{constructor({strings:e,_$litType$:t},i){let n;this.parts=[];let s=0,o=0;const l=e.length-1,a=this.parts,[u,h]=Be(e,t);if(this.el=k.createElement(u,i),$.currentNode=this.el.content,t===2||t===3){const c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(n=$.nextNode())!==null&&a.length<l;){if(n.nodeType===1){if(n.hasAttributes())for(const c of n.getAttributeNames())if(c.endsWith(fe)){const m=h[o++],f=n.getAttribute(c).split(_),y=/([.?@])?(.*)/.exec(m);a.push({type:1,index:s,name:y[2],strings:f,ctor:y[1]==="."?Qe:y[1]==="?"?We:y[1]==="@"?Fe:j}),n.removeAttribute(c)}else c.startsWith(_)&&(a.push({type:6,index:s}),n.removeAttribute(c));if(ve.test(n.tagName)){const c=n.textContent.split(_),m=c.length-1;if(m>0){n.textContent=q?q.emptyScript:"";for(let f=0;f<m;f++)n.append(c[f],O()),$.nextNode(),a.push({type:2,index:++s});n.append(c[m],O())}}}else if(n.nodeType===8)if(n.data===_e)a.push({type:2,index:s});else{let c=-1;for(;(c=n.data.indexOf(_,c+1))!==-1;)a.push({type:7,index:s}),c+=_.length-1}s++}}static createElement(e,t){const i=b.createElement("template");return i.innerHTML=e,i}}function S(r,e,t=r,i){if(e===x)return e;let n=i!==void 0?t._$Co?.[i]:t._$Cl;const s=M(e)?void 0:e._$litDirective$;return n?.constructor!==s&&(n?._$AO?.(!1),s===void 0?n=void 0:(n=new s(r),n._$AT(r,t,i)),i!==void 0?(t._$Co??(t._$Co=[]))[i]=n:t._$Cl=n),n!==void 0&&(e=S(r,n._$AS(r,e.values),n,i)),e}class Ve{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,n=(e?.creationScope??b).importNode(t,!0);$.currentNode=n;let s=$.nextNode(),o=0,l=0,a=i[0];for(;a!==void 0;){if(o===a.index){let u;a.type===2?u=new N(s,s.nextSibling,this,e):a.type===1?u=new a.ctor(s,a.name,a.strings,this,e):a.type===6&&(u=new Ge(s,this,e)),this._$AV.push(u),a=i[++l]}o!==a?.index&&(s=$.nextNode(),o++)}return $.currentNode=b,n}p(e){let t=0;for(const i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class N{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,n){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=S(this,e,t),M(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==x&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):ze(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&M(this._$AH)?this._$AA.nextSibling.data=e:this.T(b.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,n=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=k.createElement(ge(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===n)this._$AH.p(t);else{const s=new Ve(n,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=ce.get(e.strings);return t===void 0&&ce.set(e.strings,t=new k(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,n=0;for(const s of e)n===t.length?t.push(i=new N(this.O(O()),this.O(O()),this,this.options)):i=t[n],i._$AI(s),n++;n<t.length&&(this._$AR(i&&i._$AB.nextSibling,n),t.length=n)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const i=ie(e).nextSibling;ie(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class j{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,n,s){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=n,this.options=s,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=d}_$AI(e,t=this,i,n){const s=this.strings;let o=!1;if(s===void 0)e=S(this,e,t,0),o=!M(e)||e!==this._$AH&&e!==x,o&&(this._$AH=e);else{const l=e;let a,u;for(e=s[0],a=0;a<s.length-1;a++)u=S(this,l[i+a],t,a),u===x&&(u=this._$AH[a]),o||(o=!M(u)||u!==this._$AH[a]),u===d?e=d:e!==d&&(e+=(u??"")+s[a+1]),this._$AH[a]=u}o&&!n&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Qe extends j{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}}class We extends j{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}}class Fe extends j{constructor(e,t,i,n,s){super(e,t,i,n,s),this.type=5}_$AI(e,t=this){if((e=S(this,e,t,0)??d)===x)return;const i=this._$AH,n=e===d&&i!==d||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,s=e!==d&&(i===d||n);n&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Ge{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){S(this,e)}}const Ke=R.litHtmlPolyfillSupport;Ke?.(k,N),(R.litHtmlVersions??(R.litHtmlVersions=[])).push("3.3.3");const Ze=(r,e,t)=>{const i=t?.renderBefore??e;let n=i._$litPart$;if(n===void 0){const s=t?.renderBefore??null;i._$litPart$=n=new N(e.insertBefore(O(),s),s,void 0,t??{})}return n._$AI(r),n};const I=globalThis;class P extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ze(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}}P._$litElement$=!0,P.finalized=!0,I.litElementHydrateSupport?.({LitElement:P});const Je=I.litElementPolyfillSupport;Je?.({LitElement:P});(I.litElementVersions??(I.litElementVersions=[])).push("4.2.2");const Ye=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),Xe=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),et={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function w(r){return String(r??"").trim().toLowerCase()}function $e(r){const e=w(r);return e?e.replaceAll("_"," "):""}function tt(r){const e=w(r);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:et[e]??$e(e)}function rt(r){switch(r){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return $e(r)}}function it(r){if(w(r.queueRunState)!=="running")return null;const e=w(r.vacuumState),t=w(r.robotState),i=w(r.taskStatus),n=tt(r.errorCode);if(e==="error")return{phase:"error",label:n??"Error"};if(i==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:n?`Paused (${n})`:"Paused"};if(Ye.has(t))return{phase:"preparing",label:rt(t)};if(e==="returning"&&i==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(Xe.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function V(r,e){const t=String(r||"").trim();if(!t.startsWith("vacuum."))return null;const i=t.slice(7);return i?`sensor.${i}_${e}`:null}function H(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function nt(r){return String(r??"").trim()}function be(r){return nt(r).toLowerCase()}function T(r){return typeof r!="number"||!Number.isFinite(r)||r<0?null:Math.trunc(r)}function Q(r,e){return r.filter(t=>t.status===e).length}function st(r){if(!H(r))return null;const e=r.item_id,t=r.room_id,i=r.room_name,n=r.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof i!="string"||typeof n!="string"?null:{itemId:e,roomId:t,roomName:i,status:n,overrides:H(r.overrides)?{...r.overrides}:{},result:typeof r.result=="string"?r.result:null}}function ye(r){const e=be(r);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function ot(r){if(!H(r))return[];const e=r.queue_items;return Array.isArray(e)?e.flatMap(t=>{const i=st(t);return i?[i]:[]}):[]}function at(r){const e=r?.attributes,t=ot(e),i=H(e)?e:{};return{runState:be(r?.state)||"unknown",configEntryId:typeof i.config_entry_id=="string"?i.config_entry_id:null,vacuumEntityId:typeof i.vacuum_entity_id=="string"?i.vacuum_entity_id:null,pendingItems:T(i.pending_items)??Q(t,"pending"),runningItems:T(i.running_items)??Q(t,"running"),completedItems:T(i.completed_items)??Q(t,"completed"),totalItems:T(i.total_items)??t.length,items:t}}const Ae={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},lt={water_volume:2,suction_level:1,repeats:1};function we(r){if(r==null)return null;if(typeof r=="number")return Number.isFinite(r)?Math.trunc(r):null;if(typeof r=="string"){const e=Number(r.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function xe(r,e){const t={};for(const[i,n]of Object.entries(e??{}))n!=null&&(t[i]=n);for(const[i,n]of Object.entries(r??{}))n!=null&&(t[i]=n);return t}function ct(r,e,t){const i=xe(e,t);return we(i[r])??lt[r]}function ut(r,e,t){const i=ct(r,e,t),n=Ae[r].find(s=>s.value===i);return n?n.label:String(i)}function dt(r,e,t){const i=xe(e,t),n=Ae[r],s=we(i[r]),o=n.findIndex(a=>a.value===s),l=o<0?0:(o+1)%n.length;return i[r]=n[l].value,i}function ue(r){if(typeof r=="number"&&Number.isInteger(r))return r;if(typeof r!="string")return null;const e=r.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function F(r,e){if(Array.isArray(r)){for(const s of r)F(s,e);return}if(typeof r!="object"||r===null)return;const t=r,i=ue(t.id),n=typeof t.name=="string"?t.name.trim():"";i!==null&&n&&e.push({roomId:i,roomName:n});for(const[s,o]of Object.entries(t)){const l=ue(s);if(l!==null&&typeof o=="string"){const a=o.trim();if(a){e.push({roomId:l,roomName:a});continue}}F(o,e)}}function ht(r){const e=[];F(r,e);const t=new Map;for(const i of e)t.set(i.roomId,i.roomName);return Array.from(t.entries()).map(([i,n])=>({roomId:i,roomName:n})).sort((i,n)=>i.roomId-n.roomId)}const D="ha-dreame-queue-card",pt="ha-dreame-queue-card-editor",mt="HA Dreame Queue",ft="sensor.ha_dreame_queue_status",_t=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}];function vt(r){return Object.entries(r?.states??{}).filter(([e,t])=>e.startsWith("sensor.")&&Et(t)).map(([e])=>e).sort()}function gt(r){return{entity:vt(r)[0]??ft}}function $t(r,e){const t=he(e.title)||mt,i=he(e.entity)||null;if(!i)return de({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const n=r?.states[i];if(!n)return de({title:t,status:"missing",entityId:i,message:"Queue entity not found."});const s=at(n),o=bt(r,s),l=St(r,s);return{title:t,status:"ready",entityId:i,message:null,summary:wt(s,o),snapshot:s,activity:o,activeControls:At(s),canClearPending:s.pendingItems>0,rooms:l,rows:yt(s.items)}}function de({title:r,status:e,entityId:t,message:i}){return{title:r,status:e,entityId:t,message:i,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function bt(r,e){const t=e.vacuumEntityId;return!r||!t?null:it({queueRunState:e.runState,vacuumState:U(r,t),robotState:U(r,V(t,"state")),taskStatus:U(r,V(t,"task_status")),errorCode:U(r,V(t,"error"))})}function yt(r){const e=r.flatMap((n,s)=>n.status==="pending"?[s]:[]),t=e[0]??null,i=e[e.length-1]??null;return r.map((n,s)=>({itemId:n.itemId,queuePosition:s,roomName:n.roomName,status:n.status,statusLabel:ye(n.status),overrides:{...n.overrides},canRemove:n.status==="pending",canMoveUp:n.status==="pending"&&s!==t,canMoveDown:n.status==="pending"&&s!==i,overrideControls:n.status==="pending"?xt(n.overrides):[]}))}function At(r){return r.runState==="running"?[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue"},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room"}]:r.runState==="idle"&&r.pendingItems>0?[{ariaLabel:"Start queue",label:"Start",service:"start_queue"}]:[]}function wt(r,e){if(e)return e.label;switch(r.runState){case"idle":return r.pendingItems===1?"Ready to start 1 room.":r.pendingItems>1?`Ready to start ${r.pendingItems} rooms.`:"Queue is empty.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access before restarting.";case"out_of_sync":return"Queue out of sync. Review robot state before restarting.";case"manual_control":return"Manual control active.";default:return`Queue state: ${ye(r.runState)}.`}}function xt(r){return _t.map(e=>({field:e.field,label:e.label,valueLabel:ut(e.field,r,{})}))}function St(r,e){const t=e.vacuumEntityId;if(!r||!t)return[];const i=r.states[t]?.attributes;return ht(Se(i)?i.rooms:void 0)}function U(r,e){return e?r.states[e]?.state:void 0}function he(r){return String(r??"").trim()}function Se(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function Et(r){const e=r?.attributes;return Se(e)&&Array.isArray(e.queue_items)&&typeof e.config_entry_id=="string"}const z=class z extends P{constructor(){super(...arguments),this._config={}}static async getConfigElement(){return await Re(()=>import("./ha-dreame-queue-card-editor-lXmQUl9-.js"),[]),document.createElement(pt)}static getStubConfig(e){return gt(e)}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 6}render(){const e=$t(this.hass,this._config),t=e.snapshot,i=t?.configEntryId;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="activity-line">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          <div class="header-right">
            ${t?this._renderHeaderActions(e.activeControls,e.canClearPending,i):d}
            ${t?p`<span class="state-pill ${t.runState}"
                  >${this._stateLabel(t.runState)}</span
                >`:d}
          </div>
        </div>

        ${e.message?p`<div class="message">${e.message}</div>`:p`
              ${e.rooms.length?p`
                    <div class="section-title">Available rooms</div>
                    <div class="room-actions">
                      ${e.rooms.map(n=>p`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!i}
                            @click=${()=>this._addRoom(i,n.roomId,n.roomName)}
                          >
                            <ha-icon icon="mdi:plus"></ha-icon>
                            ${n.roomName}
                          </button>
                        `)}
                    </div>
                  `:d}
              <div class="queue-list">
                ${e.rows.length?e.rows.map(n=>p`
                        <div class="queue-item ${n.status}">
                          <div class="item-main">
                            <div class="item-headline">
                              <div class="item-title-block">
                                <span class="room-name"
                                  >${n.queuePosition+1}. ${n.roomName}</span
                                >
                                <span class="row-status ${n.status}">${n.statusLabel}</span>
                              </div>
                              ${this._renderQueueItemActions(n,i)}
                            </div>
                            ${n.overrideControls.length?p`
                                  <div class="item-actions">
                                    <div class="override-controls">
                                      ${n.overrideControls.map(s=>this._renderOverrideControl(n.roomName,n.itemId,n.overrides,s,i))}
                                    </div>
                                  </div>
                                `:d}
                          </div>
                        </div>
                      `):p`<div class="empty">Queue is empty.</div>`}
              </div>
            `}
      </ha-card>
    `}_renderHeaderActions(e,t,i){return!e.length&&!t?d:p`
      <div class="header-actions">
        ${e.map(n=>p`
            <button
              aria-label=${n.ariaLabel}
              class="icon-btn ${n.service==="cancel_queue"?"delete":""}"
              title=${n.ariaLabel}
              type="button"
              ?disabled=${!i}
              @click=${()=>this._callQueueService(i,n.service)}
            >
              <ha-icon icon=${this._activeControlIcon(n.service)}></ha-icon>
            </button>
          `)}
        ${t?p`
              <button
                aria-label="Clear pending queue"
                class="icon-btn"
                title="Clear pending queue"
                type="button"
                ?disabled=${!i}
                @click=${()=>this._clearPending(i)}
              >
                <ha-icon icon="mdi:playlist-remove"></ha-icon>
              </button>
            `:d}
      </div>
    `}_renderQueueItemActions(e,t){return!e.canMoveUp&&!e.canMoveDown&&!e.canRemove?d:p`
      <div class="item-queue-controls">
        ${e.canMoveUp?p`
              <button
                aria-label=${`Move ${e.roomName} up`}
                class="icon-btn"
                title="Move up"
                type="button"
                ?disabled=${!t}
                @click=${()=>this._moveItem(t,e.itemId,e.queuePosition-1)}
              >
                <ha-icon icon="mdi:arrow-up"></ha-icon>
              </button>
            `:d}
        ${e.canMoveDown?p`
              <button
                aria-label=${`Move ${e.roomName} down`}
                class="icon-btn"
                title="Move down"
                type="button"
                ?disabled=${!t}
                @click=${()=>this._moveItem(t,e.itemId,e.queuePosition+1)}
              >
                <ha-icon icon="mdi:arrow-down"></ha-icon>
              </button>
            `:d}
        ${e.canRemove?p`
              <button
                aria-label=${`Remove ${e.roomName}`}
                class="icon-btn delete"
                title="Remove"
                type="button"
                ?disabled=${!t}
                @click=${()=>this._removeItem(t,e.itemId)}
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            `:d}
      </div>
    `}_renderOverrideControl(e,t,i,n,s){return p`
      <button
        aria-label=${`Cycle ${e} ${this._overrideAriaField(n.field)}`}
        class="override-btn"
        title=${`${n.label}: ${n.valueLabel}`}
        type="button"
        ?disabled=${!s}
        @click=${()=>this._updateOverrides(s,t,n.field,i)}
      >
        <ha-icon icon=${this._overrideIcon(n.field,n.valueLabel)}></ha-icon>
        ${this._renderOverrideValue(n.field,n.valueLabel)}
      </button>
    `}_renderOverrideValue(e,t){if(e==="repeats")return p`<span>${t}</span>`;const i=e==="water_volume"?3:4;return this._renderBars(i,this._overrideActiveBars(e,t))}_renderBars(e,t){const i=Math.max(0,Math.min(e,t));return p`
      <span class="override-bars" aria-hidden="true">
        ${Array.from({length:e},(n,s)=>{const o=6+s*2,l=s<i;return p`
            <span
              class="override-bar ${l?"active":""}"
              style=${`height:${o}px;`}
            ></span>
          `})}
      </span>
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_activeControlIcon(e){return e==="start_queue"?"mdi:play":e==="skip_current_room"?"mdi:skip-next":"mdi:stop"}_overrideIcon(e,t){return e==="water_volume"?t==="Off"?"mdi:water-off":"mdi:water-percent":e==="suction_level"?t==="Off"?"mdi:fan-off":"mdi:fan":"mdi:repeat"}_overrideActiveBars(e,t){return t==="Off"?0:e==="water_volume"?{Min:1,Med:2,Max:3}[t]??0:e==="suction_level"?{Min:1,Med:2,Max:3,Turbo:4}[t]??0:0}_addRoom(e,t,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:i})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:i})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}_callQueueService(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame",t,{config_entry_id:e})}_updateOverrides(e,t,i,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:dt(i,n,{})})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};z.properties={hass:{attribute:!1},_config:{state:!0}},z.styles=Pe`
    :host {
      display: block;
    }

    ha-card {
      display: block;
      padding: 14px;
    }

    .header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
    }

    .header-right {
      align-items: center;
      display: inline-flex;
      gap: 6px;
      min-width: 0;
    }

    .header-actions {
      align-items: center;
      display: inline-flex;
      gap: 4px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .activity-line {
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.25;
      margin: 3px 0 0;
      overflow-wrap: anywhere;
    }

    .state-pill {
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.2;
      padding: 4px 9px;
      white-space: nowrap;
    }

    .state-pill.running {
      border-color: var(--state-active-color, #2e7d32);
      color: var(--state-active-color, #2e7d32);
    }

    .state-pill.blocked,
    .state-pill.out_of_sync,
    .state-pill.error {
      border-color: var(--error-color, #d32f2f);
      color: var(--error-color, #d32f2f);
    }

    .message {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.35;
      padding: 10px;
    }

    .empty {
      color: var(--secondary-text-color);
      font-size: 0.9rem;
      line-height: 1.35;
    }

    .room-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: inherit;
      font-size: 0.84rem;
      line-height: 1;
      max-width: 100%;
      overflow: hidden;
      padding: 7px 11px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .room-chip:not(:disabled):hover,
    .override-btn:not(:disabled):hover,
    .icon-btn:not(:disabled):hover {
      background: color-mix(in srgb, var(--primary-color, #03a9f4) 10%, transparent);
    }

    .queue-list {
      display: grid;
      gap: 8px;
    }

    .queue-item {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr);
      padding: 8px 10px;
    }

    .queue-item.running {
      border-color: color-mix(in srgb, var(--state-active-color, #2e7d32) 45%, var(--divider-color));
    }

    .item-main,
    .item-title-block {
      min-width: 0;
    }

    .item-headline {
      align-items: center;
      display: flex;
      gap: 8px;
      justify-content: space-between;
    }

    .room-name {
      display: block;
      font-size: 0.96rem;
      font-weight: 600;
      line-height: 1.25;
      margin: 0;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      text-align: left;
      text-transform: lowercase;
      white-space: nowrap;
    }

    .row-status.running {
      color: var(--state-active-color, #2e7d32);
    }

    .row-status.canceled,
    .row-status.blocked,
    .row-status.out_of_sync {
      color: var(--error-color, #d32f2f);
    }

    .item-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    .item-queue-controls {
      align-items: center;
      display: flex;
      gap: 4px;
      justify-content: flex-end;
    }

    .override-controls {
      display: flex;
      flex: 1;
      flex-wrap: wrap;
      gap: 4px;
    }

    .icon-btn {
      align-items: center;
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      font-family: inherit;
      height: 32px;
      justify-content: center;
      padding: 0;
      width: 32px;
    }

    .icon-btn.delete {
      color: var(--error-color, #d32f2f);
    }

    .icon-btn:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
      opacity: 0.45;
    }

    .override-btn {
      align-items: center;
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      font-family: inherit;
      font-size: 0.72rem;
      gap: 6px;
      justify-content: center;
      line-height: 1.2;
      min-height: 26px;
      min-width: 68px;
      padding: 2px 8px;
      white-space: nowrap;
    }

    .override-btn:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
      opacity: 0.5;
    }

    .override-bars {
      align-items: flex-end;
      display: inline-flex;
      gap: 2px;
    }

    .override-bar {
      background: color-mix(in srgb, var(--divider-color) 80%, transparent);
      border-radius: 999px;
      width: 3px;
    }

    .override-bar.active {
      background: var(--primary-color, #03a9f4);
    }
  `;let G=z;customElements.get(D)||customElements.define(D,G);window.customCards=window.customCards??[];window.customCards.some(r=>r.type===D)||window.customCards.push({type:D,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});export{pt as C,mt as D,Pe as a,p as b,P as i,vt as q};
