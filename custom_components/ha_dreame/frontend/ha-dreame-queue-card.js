const xe="modulepreload",Ce=function(n){return"/"+n},Y={},Ie=function(e,t,r){let i=Promise.resolve();if(t&&t.length>0){let a=function(u){return Promise.all(u.map(h=>Promise.resolve(h).then(c=>({status:"fulfilled",value:c}),c=>({status:"rejected",reason:c}))))};document.getElementsByTagName("link");const o=document.querySelector("meta[property=csp-nonce]"),l=o?.nonce||o?.getAttribute("nonce");i=a(t.map(u=>{if(u=Ce(u),u in Y)return;Y[u]=!0;const h=u.endsWith(".css"),c=h?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${u}"]${c}`))return;const p=document.createElement("link");if(p.rel=h?"stylesheet":xe,h||(p.as="script"),p.crossOrigin="",p.href=u,l&&p.setAttribute("nonce",l),document.head.appendChild(p),h)return new Promise((f,b)=>{p.addEventListener("load",f),p.addEventListener("error",()=>b(new Error(`Unable to preload CSS for ${u}`)))})}))}function s(o){const l=new Event("vite:preloadError",{cancelable:!0});if(l.payload=o,window.dispatchEvent(l),!l.defaultPrevented)throw o}return i.then(o=>{for(const l of o||[])l.status==="rejected"&&s(l.reason);return e().catch(s)})};const L=globalThis,K=L.ShadowRoot&&(L.ShadyCSS===void 0||L.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),X=new WeakMap;let pe=class{constructor(e,t,r){if(this._$cssResult$=!0,r!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(K&&e===void 0){const r=t!==void 0&&t.length===1;r&&(e=X.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),r&&X.set(t,e))}return e}toString(){return this.cssText}};const Re=n=>new pe(typeof n=="string"?n:n+"",void 0,Z),Pe=(n,...e)=>{const t=n.length===1?n[0]:e.reduce((r,i,s)=>r+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[s+1],n[0]);return new pe(t,n,Z)},Ne=(n,e)=>{if(K)n.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const r=document.createElement("style"),i=L.litNonce;i!==void 0&&r.setAttribute("nonce",i),r.textContent=t.cssText,n.appendChild(r)}},ee=K?n=>n:n=>n instanceof CSSStyleSheet?(e=>{let t="";for(const r of e.cssRules)t+=r.cssText;return Re(t)})(n):n;const{is:Oe,defineProperty:ke,getOwnPropertyDescriptor:Me,getOwnPropertyNames:Te,getOwnPropertySymbols:Ue,getPrototypeOf:Le}=Object,g=globalThis,te=g.trustedTypes,qe=te?te.emptyScript:"",De=g.reactiveElementPolyfillSupport,C=(n,e)=>n,W={toAttribute(n,e){switch(e){case Boolean:n=n?qe:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,e){let t=n;switch(e){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},me=(n,e)=>!Oe(n,e),re={attribute:!0,type:String,converter:W,reflect:!1,useDefault:!1,hasChanged:me};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),g.litPropertyMetadata??(g.litPropertyMetadata=new WeakMap);let A=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=re){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const r=Symbol(),i=this.getPropertyDescriptor(e,r,t);i!==void 0&&ke(this.prototype,e,i)}}static getPropertyDescriptor(e,t,r){const{get:i,set:s}=Me(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){const l=i?.call(this);s?.call(this,o),this.requestUpdate(e,l,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??re}static _$Ei(){if(this.hasOwnProperty(C("elementProperties")))return;const e=Le(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(C("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(C("properties"))){const t=this.properties,r=[...Te(t),...Ue(t)];for(const i of r)this.createProperty(i,t[i])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[r,i]of t)this.elementProperties.set(r,i)}this._$Eh=new Map;for(const[t,r]of this.elementProperties){const i=this._$Eu(t,r);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const r=new Set(e.flat(1/0).reverse());for(const i of r)t.unshift(ee(i))}else e!==void 0&&t.push(ee(e));return t}static _$Eu(e,t){const r=t.attribute;return r===!1?void 0:typeof r=="string"?r:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const r of t.keys())this.hasOwnProperty(r)&&(e.set(r,this[r]),delete this[r]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ne(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,r){this._$AK(e,r)}_$ET(e,t){const r=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,r);if(i!==void 0&&r.reflect===!0){const s=(r.converter?.toAttribute!==void 0?r.converter:W).toAttribute(t,r.type);this._$Em=e,s==null?this.removeAttribute(i):this.setAttribute(i,s),this._$Em=null}}_$AK(e,t){const r=this.constructor,i=r._$Eh.get(e);if(i!==void 0&&this._$Em!==i){const s=r.getPropertyOptions(i),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:W;this._$Em=i;const l=o.fromAttribute(t,s.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(e,t,r,i=!1,s){if(e!==void 0){const o=this.constructor;if(i===!1&&(s=this[e]),r??(r=o.getPropertyOptions(e)),!((r.hasChanged??me)(s,t)||r.useDefault&&r.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,r))))return;this.C(e,t,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:r,reflect:i,wrapped:s},o){r&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||r||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[i,s]of this._$Ep)this[i]=s;this._$Ep=void 0}const r=this.constructor.elementProperties;if(r.size>0)for(const[i,s]of r){const{wrapped:o}=s,l=this[i];o!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,s,l)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(t)):this._$EM()}catch(r){throw e=!1,this._$EM(),r}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[C("elementProperties")]=new Map,A[C("finalized")]=new Map,De?.({ReactiveElement:A}),(g.reactiveElementVersions??(g.reactiveElementVersions=[])).push("2.1.2");const I=globalThis,ne=n=>n,q=I.trustedTypes,ie=q?q.createPolicy("lit-html",{createHTML:n=>n}):void 0,fe="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,_e="?"+_,He=`<${_e}>`,y=document,N=()=>y.createComment(""),O=n=>n===null||typeof n!="object"&&typeof n!="function",J=Array.isArray,ze=n=>J(n)||typeof n?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,x=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,se=/-->/g,oe=/>/g,$=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ae=/'/g,le=/"/g,ge=/^(?:script|style|textarea|title)$/i,je=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),m=je(1),S=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),ce=new WeakMap,v=y.createTreeWalker(y,129);function $e(n,e){if(!J(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return ie!==void 0?ie.createHTML(e):e}const Be=(n,e)=>{const t=n.length-1,r=[];let i,s=e===2?"<svg>":e===3?"<math>":"",o=x;for(let l=0;l<t;l++){const a=n[l];let u,h,c=-1,p=0;for(;p<a.length&&(o.lastIndex=p,h=o.exec(a),h!==null);)p=o.lastIndex,o===x?h[1]==="!--"?o=se:h[1]!==void 0?o=oe:h[2]!==void 0?(ge.test(h[2])&&(i=RegExp("</"+h[2],"g")),o=$):h[3]!==void 0&&(o=$):o===$?h[0]===">"?(o=i??x,c=-1):h[1]===void 0?c=-2:(c=o.lastIndex-h[2].length,u=h[1],o=h[3]===void 0?$:h[3]==='"'?le:ae):o===le||o===ae?o=$:o===se||o===oe?o=x:(o=$,i=void 0);const f=o===$&&n[l+1].startsWith("/>")?" ":"";s+=o===x?a+He:c>=0?(r.push(u),a.slice(0,c)+fe+a.slice(c)+_+f):a+_+(c===-2?l:f)}return[$e(n,s+(n[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),r]};class k{constructor({strings:e,_$litType$:t},r){let i;this.parts=[];let s=0,o=0;const l=e.length-1,a=this.parts,[u,h]=Be(e,t);if(this.el=k.createElement(u,r),v.currentNode=this.el.content,t===2||t===3){const c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(i=v.nextNode())!==null&&a.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(const c of i.getAttributeNames())if(c.endsWith(fe)){const p=h[o++],f=i.getAttribute(c).split(_),b=/([.?@])?(.*)/.exec(p);a.push({type:1,index:s,name:b[2],strings:f,ctor:b[1]==="."?Qe:b[1]==="?"?We:b[1]==="@"?Fe:j}),i.removeAttribute(c)}else c.startsWith(_)&&(a.push({type:6,index:s}),i.removeAttribute(c));if(ge.test(i.tagName)){const c=i.textContent.split(_),p=c.length-1;if(p>0){i.textContent=q?q.emptyScript:"";for(let f=0;f<p;f++)i.append(c[f],N()),v.nextNode(),a.push({type:2,index:++s});i.append(c[p],N())}}}else if(i.nodeType===8)if(i.data===_e)a.push({type:2,index:s});else{let c=-1;for(;(c=i.data.indexOf(_,c+1))!==-1;)a.push({type:7,index:s}),c+=_.length-1}s++}}static createElement(e,t){const r=y.createElement("template");return r.innerHTML=e,r}}function E(n,e,t=n,r){if(e===S)return e;let i=r!==void 0?t._$Co?.[r]:t._$Cl;const s=O(e)?void 0:e._$litDirective$;return i?.constructor!==s&&(i?._$AO?.(!1),s===void 0?i=void 0:(i=new s(n),i._$AT(n,t,r)),r!==void 0?(t._$Co??(t._$Co=[]))[r]=i:t._$Cl=i),i!==void 0&&(e=E(n,i._$AS(n,e.values),i,r)),e}class Ve{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:r}=this._$AD,i=(e?.creationScope??y).importNode(t,!0);v.currentNode=i;let s=v.nextNode(),o=0,l=0,a=r[0];for(;a!==void 0;){if(o===a.index){let u;a.type===2?u=new M(s,s.nextSibling,this,e):a.type===1?u=new a.ctor(s,a.name,a.strings,this,e):a.type===6&&(u=new Ge(s,this,e)),this._$AV.push(u),a=r[++l]}o!==a?.index&&(s=v.nextNode(),o++)}return v.currentNode=y,i}p(e){let t=0;for(const r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(e,r,t),t+=r.strings.length-2):r._$AI(e[t])),t++}}class M{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,r,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=r,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=E(this,e,t),O(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==S&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):ze(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&O(this._$AH)?this._$AA.nextSibling.data=e:this.T(y.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:r}=e,i=typeof r=="number"?this._$AC(e):(r.el===void 0&&(r.el=k.createElement($e(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===i)this._$AH.p(t);else{const s=new Ve(i,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=ce.get(e.strings);return t===void 0&&ce.set(e.strings,t=new k(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let r,i=0;for(const s of e)i===t.length?t.push(r=new M(this.O(N()),this.O(N()),this,this.options)):r=t[i],r._$AI(s),i++;i<t.length&&(this._$AR(r&&r._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const r=ne(e).nextSibling;ne(e).remove(),e=r}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class j{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,r,i,s){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=s,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=d}_$AI(e,t=this,r,i){const s=this.strings;let o=!1;if(s===void 0)e=E(this,e,t,0),o=!O(e)||e!==this._$AH&&e!==S,o&&(this._$AH=e);else{const l=e;let a,u;for(e=s[0],a=0;a<s.length-1;a++)u=E(this,l[r+a],t,a),u===S&&(u=this._$AH[a]),o||(o=!O(u)||u!==this._$AH[a]),u===d?e=d:e!==d&&(e+=(u??"")+s[a+1]),this._$AH[a]=u}o&&!i&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Qe extends j{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}}class We extends j{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}}class Fe extends j{constructor(e,t,r,i,s){super(e,t,r,i,s),this.type=5}_$AI(e,t=this){if((e=E(this,e,t,0)??d)===S)return;const r=this._$AH,i=e===d&&r!==d||e.capture!==r.capture||e.once!==r.once||e.passive!==r.passive,s=e!==d&&(r===d||i);i&&this.element.removeEventListener(this.name,this,r),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Ge{constructor(e,t,r){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(e){E(this,e)}}const Ke=I.litHtmlPolyfillSupport;Ke?.(k,M),(I.litHtmlVersions??(I.litHtmlVersions=[])).push("3.3.3");const Ze=(n,e,t)=>{const r=t?.renderBefore??e;let i=r._$litPart$;if(i===void 0){const s=t?.renderBefore??null;r._$litPart$=i=new M(e.insertBefore(N(),s),s,void 0,t??{})}return i._$AI(n),i};const R=globalThis;class P extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ze(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return S}}P._$litElement$=!0,P.finalized=!0,R.litElementHydrateSupport?.({LitElement:P});const Je=R.litElementPolyfillSupport;Je?.({LitElement:P});(R.litElementVersions??(R.litElementVersions=[])).push("4.2.2");const Ye=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),Xe=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),et={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function w(n){return String(n??"").trim().toLowerCase()}function ve(n){const e=w(n);return e?e.replaceAll("_"," "):""}function tt(n){const e=w(n);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:et[e]??ve(e)}function rt(n){switch(n){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return ve(n)}}function nt(n){if(w(n.queueRunState)!=="running")return null;const e=w(n.vacuumState),t=w(n.robotState),r=w(n.taskStatus),i=tt(n.errorCode);if(e==="error")return{phase:"error",label:i??"Error"};if(r==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:i?`Paused (${i})`:"Paused"};if(Ye.has(t))return{phase:"preparing",label:rt(t)};if(e==="returning"&&r==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(Xe.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function V(n,e){const t=String(n||"").trim();if(!t.startsWith("vacuum."))return null;const r=t.slice(7);return r?`sensor.${r}_${e}`:null}function D(n){return typeof n=="object"&&n!==null&&!Array.isArray(n)}function it(n){return String(n??"").trim()}function ye(n){return it(n).toLowerCase()}function T(n){return typeof n!="number"||!Number.isFinite(n)||n<0?null:Math.trunc(n)}function Q(n,e){return n.filter(t=>t.status===e).length}function st(n){if(!D(n))return null;const e=n.item_id,t=n.room_id,r=n.room_name,i=n.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof r!="string"||typeof i!="string"?null:{itemId:e,roomId:t,roomName:r,status:i,overrides:D(n.overrides)?{...n.overrides}:{},result:typeof n.result=="string"?n.result:null}}function be(n){const e=ye(n);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function ot(n){if(!D(n))return[];const e=n.queue_items;return Array.isArray(e)?e.flatMap(t=>{const r=st(t);return r?[r]:[]}):[]}function at(n){const e=n?.attributes,t=ot(e),r=D(e)?e:{};return{runState:ye(n?.state)||"unknown",configEntryId:typeof r.config_entry_id=="string"?r.config_entry_id:null,vacuumEntityId:typeof r.vacuum_entity_id=="string"?r.vacuum_entity_id:null,pendingItems:T(r.pending_items)??Q(t,"pending"),runningItems:T(r.running_items)??Q(t,"running"),completedItems:T(r.completed_items)??Q(t,"completed"),totalItems:T(r.total_items)??t.length,items:t}}const Ae={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},lt={water_volume:2,suction_level:1,repeats:1};function we(n){if(n==null)return null;if(typeof n=="number")return Number.isFinite(n)?Math.trunc(n):null;if(typeof n=="string"){const e=Number(n.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function Se(n,e){const t={};for(const[r,i]of Object.entries(e??{}))i!=null&&(t[r]=i);for(const[r,i]of Object.entries(n??{}))i!=null&&(t[r]=i);return t}function ct(n,e,t){const r=Se(e,t);return we(r[n])??lt[n]}function ut(n,e,t){const r=ct(n,e,t),i=Ae[n].find(s=>s.value===r);return i?i.label:String(r)}function dt(n,e,t){const r=Se(e,t),i=Ae[n],s=we(r[n]),o=i.findIndex(a=>a.value===s),l=o<0?0:(o+1)%i.length;return r[n]=i[l].value,r}function ue(n){if(typeof n=="number"&&Number.isInteger(n))return n;if(typeof n!="string")return null;const e=n.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function F(n,e){if(Array.isArray(n)){for(const s of n)F(s,e);return}if(typeof n!="object"||n===null)return;const t=n,r=ue(t.id),i=typeof t.name=="string"?t.name.trim():"";r!==null&&i&&e.push({roomId:r,roomName:i});for(const[s,o]of Object.entries(t)){const l=ue(s);if(l!==null&&typeof o=="string"){const a=o.trim();if(a){e.push({roomId:l,roomName:a});continue}}F(o,e)}}function ht(n){const e=[];F(n,e);const t=new Map;for(const r of e)t.set(r.roomId,r.roomName);return Array.from(t.entries()).map(([r,i])=>({roomId:r,roomName:i})).sort((r,i)=>r.roomId-i.roomId)}const H="ha-dreame-queue-card",pt="ha-dreame-queue-card-editor",mt="HA Dreame Queue",ft="sensor.ha_dreame_queue_status",_t=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}];function gt(n){return Object.entries(n?.states??{}).filter(([e,t])=>e.startsWith("sensor.")&&xt(t)).map(([e])=>e).sort()}function $t(n){return{entity:gt(n)[0]??ft}}function vt(n,e){const t=he(e.title)||mt,r=he(e.entity)||null;if(!r)return de({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const i=n?.states[r];if(!i)return de({title:t,status:"missing",entityId:r,message:"Queue entity not found."});const s=at(i),o=yt(n,s),l=Et(n,s);return{title:t,status:"ready",entityId:r,message:null,summary:wt(s,o),snapshot:s,activity:o,activeControls:At(s),canClearPending:s.pendingItems>0,rooms:l,rows:bt(s.items)}}function de({title:n,status:e,entityId:t,message:r}){return{title:n,status:e,entityId:t,message:r,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function yt(n,e){const t=e.vacuumEntityId;return!n||!t?null:nt({queueRunState:e.runState,vacuumState:U(n,t),robotState:U(n,V(t,"state")),taskStatus:U(n,V(t,"task_status")),errorCode:U(n,V(t,"error"))})}function bt(n){const e=n.flatMap((i,s)=>i.status==="pending"?[s]:[]),t=e[0]??null,r=e[e.length-1]??null;return n.map((i,s)=>({itemId:i.itemId,queuePosition:s,roomName:i.roomName,status:i.status,statusLabel:be(i.status),overrides:{...i.overrides},canRemove:i.status==="pending",canMoveUp:i.status==="pending"&&s!==t,canMoveDown:i.status==="pending"&&s!==r,overrideControls:i.status==="pending"?St(i.overrides):[]}))}function At(n){return n.runState==="running"?[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue"},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room"}]:n.runState==="idle"&&n.pendingItems>0?[{ariaLabel:"Start queue",label:"Start",service:"start_queue"}]:[]}function wt(n,e){if(e)return e.label;switch(n.runState){case"idle":return n.pendingItems===1?"Ready to start 1 room.":n.pendingItems>1?`Ready to start ${n.pendingItems} rooms.`:"Queue is empty.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access before restarting.";case"out_of_sync":return"Queue out of sync. Review robot state before restarting.";case"manual_control":return"Manual control active.";default:return`Queue state: ${be(n.runState)}.`}}function St(n){return _t.map(e=>({field:e.field,label:e.label,valueLabel:ut(e.field,n,{})}))}function Et(n,e){const t=e.vacuumEntityId;if(!n||!t)return[];const r=n.states[t]?.attributes;return ht(Ee(r)?r.rooms:void 0)}function U(n,e){return e?n.states[e]?.state:void 0}function he(n){return String(n??"").trim()}function Ee(n){return typeof n=="object"&&n!==null&&!Array.isArray(n)}function xt(n){const e=n?.attributes;return Ee(e)&&Array.isArray(e.queue_items)&&typeof e.config_entry_id=="string"}const z=class z extends P{constructor(){super(...arguments),this._config={}}static async getConfigElement(){return await Ie(()=>import("./ha-dreame-queue-card-editor-lXmQUl9-.js"),[]),document.createElement(pt)}static getStubConfig(e){return $t(e)}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 3}render(){const e=vt(this.hass,this._config),t=e.snapshot;return m`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="subtitle">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          ${t?m`<span class="state-pill ${t.runState}"
                >${this._stateLabel(t.runState)}</span
              >`:d}
        </div>

        ${e.message?m`<div class="message">${e.message}</div>`:m`
              <div class="counts">
                ${this._count("Pending",t?.pendingItems??0)}
                ${this._count("Running",t?.runningItems??0)}
                ${this._count("Done",t?.completedItems??0)}
                ${this._count("Total",t?.totalItems??0)}
              </div>
              ${e.activeControls.length||e.canClearPending?m`
                    <div class="queue-actions">
                      ${e.activeControls.map(r=>m`
                          <button
                            aria-label=${r.ariaLabel}
                            class="row-action"
                            type="button"
                            ?disabled=${!t?.configEntryId}
                            @click=${()=>this._callQueueService(t?.configEntryId,r.service)}
                          >
                            ${r.label}
                          </button>
                        `)}
                      ${e.canClearPending?m`
                            <button
                              aria-label="Clear pending queue"
                              class="row-action"
                              type="button"
                              ?disabled=${!t?.configEntryId}
                              @click=${()=>this._clearPending(t?.configEntryId)}
                            >
                              Clear pending
                            </button>
                          `:d}
                    </div>
                  `:d}
              <div class="queue-list">
                ${e.rows.length?e.rows.map(r=>m`
                        <div class="queue-row">
                          <span class="room-name">${r.roomName}</span>
                          <div class="row-actions">
                            <span class="row-status">${r.statusLabel}</span>
                            ${r.overrideControls.map(i=>m`
                                <button
                                  aria-label=${`Cycle ${r.roomName} ${this._overrideAriaField(i.field)}`}
                                  class="row-action"
                                  type="button"
                                  ?disabled=${!t?.configEntryId}
                                  @click=${()=>this._updateOverrides(t?.configEntryId,r.itemId,i.field,r.overrides)}
                                >
                                  ${i.label} ${i.valueLabel}
                                </button>
                              `)}
                            ${r.canMoveUp?m`
                                  <button
                                    aria-label=${`Move ${r.roomName} up`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._moveItem(t?.configEntryId,r.itemId,r.queuePosition-1)}
                                  >
                                    Up
                                  </button>
                                `:d}
                            ${r.canMoveDown?m`
                                  <button
                                    aria-label=${`Move ${r.roomName} down`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._moveItem(t?.configEntryId,r.itemId,r.queuePosition+1)}
                                  >
                                    Down
                                  </button>
                                `:d}
                            ${r.canRemove?m`
                                  <button
                                    aria-label=${`Remove ${r.roomName}`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._removeItem(t?.configEntryId,r.itemId)}
                                  >
                                    Remove
                                  </button>
                                `:d}
                          </div>
                        </div>
                      `):m`<div class="message">Queue is empty.</div>`}
              </div>
              ${e.rooms.length?m`
                    <div class="section-title">Available rooms</div>
                    <div class="room-catalog">
                      ${e.rooms.map(r=>m`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!t?.configEntryId}
                            @click=${()=>this._addRoom(t?.configEntryId,r.roomId,r.roomName)}
                          >
                            ${r.roomName}
                          </button>
                        `)}
                    </div>
                  `:d}
            `}
      </ha-card>
    `}_count(e,t){return m`
      <div class="count">
        <span class="count-value">${t}</span>
        <span class="count-label">${e}</span>
      </div>
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_addRoom(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:r})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:r})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}_callQueueService(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame",t,{config_entry_id:e})}_updateOverrides(e,t,r,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:dt(r,i,{})})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};z.properties={hass:{attribute:!1},_config:{state:!0}},z.styles=Pe`
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
      align-items: start;
      gap: 10px;
      margin-bottom: 12px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .subtitle {
      margin: 3px 0 0;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
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

    .counts {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 8px;
    }

    .count {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      min-width: 0;
      padding: 7px 8px;
    }

    .count-value {
      display: block;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.1;
    }

    .count-label {
      color: var(--secondary-text-color);
      display: block;
      font-size: 0.72rem;
      line-height: 1.2;
      margin-top: 3px;
      overflow-wrap: anywhere;
    }

    .queue-list {
      display: grid;
      gap: 6px;
    }

    .queue-actions {
      display: flex;
      justify-content: flex-end;
      margin: 0 0 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-catalog {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.78rem;
      line-height: 1.2;
      max-width: 100%;
      overflow: hidden;
      padding: 5px 9px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .queue-row {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      min-height: 34px;
      padding: 7px 9px;
    }

    .room-name {
      font-size: 0.88rem;
      font-weight: 600;
      line-height: 1.25;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      white-space: nowrap;
    }

    .row-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: flex-end;
    }

    .row-action {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.74rem;
      line-height: 1.2;
      padding: 3px 8px;
      white-space: nowrap;
    }

    .row-action:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }
  `;let G=z;customElements.get(H)||customElements.define(H,G);window.customCards=window.customCards??[];window.customCards.some(n=>n.type===H)||window.customCards.push({type:H,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});export{pt as C,mt as D,Pe as a,m as b,P as i,gt as q};
