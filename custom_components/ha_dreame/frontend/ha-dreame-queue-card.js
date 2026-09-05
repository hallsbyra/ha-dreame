const ke="modulepreload",Ne=function(i){return"/"+i},te={},Pe=function(e,t,r){let n=Promise.resolve();if(t&&t.length>0){let l=function(d){return Promise.all(d.map(h=>Promise.resolve(h).then(u=>({status:"fulfilled",value:u}),u=>({status:"rejected",reason:u}))))};document.getElementsByTagName("link");const o=document.querySelector("meta[property=csp-nonce]"),a=o?.nonce||o?.getAttribute("nonce");n=l(t.map(d=>{if(d=Ne(d),d in te)return;te[d]=!0;const h=d.endsWith(".css"),u=h?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${d}"]${u}`))return;const m=document.createElement("link");if(m.rel=h?"stylesheet":ke,h||(m.as="script"),m.crossOrigin="",m.href=d,a&&m.setAttribute("nonce",a),document.head.appendChild(m),h)return new Promise((f,y)=>{m.addEventListener("load",f),m.addEventListener("error",()=>y(new Error(`Unable to preload CSS for ${d}`)))})}))}function s(o){const a=new Event("vite:preloadError",{cancelable:!0});if(a.payload=o,window.dispatchEvent(a),!a.defaultPrevented)throw o}return n.then(o=>{for(const a of o||[])a.status==="rejected"&&s(a.reason);return e().catch(s)})};const U=globalThis,Z=U.ShadowRoot&&(U.ShadyCSS===void 0||U.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,J=Symbol(),re=new WeakMap;let _e=class{constructor(e,t,r){if(this._$cssResult$=!0,r!==J)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(Z&&e===void 0){const r=t!==void 0&&t.length===1;r&&(e=re.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),r&&re.set(t,e))}return e}toString(){return this.cssText}};const Me=i=>new _e(typeof i=="string"?i:i+"",void 0,J),Te=(i,...e)=>{const t=i.length===1?i[0]:e.reduce((r,n,s)=>r+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+i[s+1],i[0]);return new _e(t,i,J)},Le=(i,e)=>{if(Z)i.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const r=document.createElement("style"),n=U.litNonce;n!==void 0&&r.setAttribute("nonce",n),r.textContent=t.cssText,i.appendChild(r)}},ie=Z?i=>i:i=>i instanceof CSSStyleSheet?(e=>{let t="";for(const r of e.cssRules)t+=r.cssText;return Me(t)})(i):i;const{is:qe,defineProperty:Ue,getOwnPropertyDescriptor:He,getOwnPropertyNames:ze,getOwnPropertySymbols:De,getPrototypeOf:Ve}=Object,_=globalThis,ne=_.trustedTypes,je=ne?ne.emptyScript:"",Be=_.reactiveElementPolyfillSupport,R=(i,e)=>i,F={toAttribute(i,e){switch(e){case Boolean:i=i?je:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,e){let t=i;switch(e){case Boolean:t=i!==null;break;case Number:t=i===null?null:Number(i);break;case Object:case Array:try{t=JSON.parse(i)}catch{t=null}}return t}},ge=(i,e)=>!qe(i,e),se={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:ge};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),_.litPropertyMetadata??(_.litPropertyMetadata=new WeakMap);let A=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=se){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const r=Symbol(),n=this.getPropertyDescriptor(e,r,t);n!==void 0&&Ue(this.prototype,e,n)}}static getPropertyDescriptor(e,t,r){const{get:n,set:s}=He(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:n,set(o){const a=n?.call(this);s?.call(this,o),this.requestUpdate(e,a,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??se}static _$Ei(){if(this.hasOwnProperty(R("elementProperties")))return;const e=Ve(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(R("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(R("properties"))){const t=this.properties,r=[...ze(t),...De(t)];for(const n of r)this.createProperty(n,t[n])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[r,n]of t)this.elementProperties.set(r,n)}this._$Eh=new Map;for(const[t,r]of this.elementProperties){const n=this._$Eu(t,r);n!==void 0&&this._$Eh.set(n,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const r=new Set(e.flat(1/0).reverse());for(const n of r)t.unshift(ie(n))}else e!==void 0&&t.push(ie(e));return t}static _$Eu(e,t){const r=t.attribute;return r===!1?void 0:typeof r=="string"?r:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const r of t.keys())this.hasOwnProperty(r)&&(e.set(r,this[r]),delete this[r]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Le(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,r){this._$AK(e,r)}_$ET(e,t){const r=this.constructor.elementProperties.get(e),n=this.constructor._$Eu(e,r);if(n!==void 0&&r.reflect===!0){const s=(r.converter?.toAttribute!==void 0?r.converter:F).toAttribute(t,r.type);this._$Em=e,s==null?this.removeAttribute(n):this.setAttribute(n,s),this._$Em=null}}_$AK(e,t){const r=this.constructor,n=r._$Eh.get(e);if(n!==void 0&&this._$Em!==n){const s=r.getPropertyOptions(n),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:F;this._$Em=n;const a=o.fromAttribute(t,s.type);this[n]=a??this._$Ej?.get(n)??a,this._$Em=null}}requestUpdate(e,t,r,n=!1,s){if(e!==void 0){const o=this.constructor;if(n===!1&&(s=this[e]),r??(r=o.getPropertyOptions(e)),!((r.hasChanged??ge)(s,t)||r.useDefault&&r.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,r))))return;this.C(e,t,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:r,reflect:n,wrapped:s},o){r&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||r||(t=void 0),this._$AL.set(e,t)),n===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[n,s]of this._$Ep)this[n]=s;this._$Ep=void 0}const r=this.constructor.elementProperties;if(r.size>0)for(const[n,s]of r){const{wrapped:o}=s,a=this[n];o!==!0||this._$AL.has(n)||a===void 0||this.C(n,void 0,s,a)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(t)):this._$EM()}catch(r){throw e=!1,this._$EM(),r}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[R("elementProperties")]=new Map,A[R("finalized")]=new Map,Be?.({ReactiveElement:A}),(_.reactiveElementVersions??(_.reactiveElementVersions=[])).push("2.1.2");const I=globalThis,oe=i=>i,H=I.trustedTypes,ae=H?H.createPolicy("lit-html",{createHTML:i=>i}):void 0,be="$lit$",v=`lit$${Math.random().toFixed(9).slice(2)}$`,$e="?"+v,We=`<${$e}>`,$=document,P=()=>$.createComment(""),M=i=>i===null||typeof i!="object"&&typeof i!="function",X=Array.isArray,Qe=i=>X(i)||typeof i?.[Symbol.iterator]=="function",W=`[ 	
\f\r]`,C=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,le=/-->/g,ue=/>/g,g=RegExp(`>|${W}(?:([^\\s"'>=/]+)(${W}*=${W}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ce=/'/g,de=/"/g,ye=/^(?:script|style|textarea|title)$/i,Fe=i=>(e,...t)=>({_$litType$:i,strings:e,values:t}),p=Fe(1),w=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),he=new WeakMap,b=$.createTreeWalker($,129);function Ae(i,e){if(!X(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ae!==void 0?ae.createHTML(e):e}const Ge=(i,e)=>{const t=i.length-1,r=[];let n,s=e===2?"<svg>":e===3?"<math>":"",o=C;for(let a=0;a<t;a++){const l=i[a];let d,h,u=-1,m=0;for(;m<l.length&&(o.lastIndex=m,h=o.exec(l),h!==null);)m=o.lastIndex,o===C?h[1]==="!--"?o=le:h[1]!==void 0?o=ue:h[2]!==void 0?(ye.test(h[2])&&(n=RegExp("</"+h[2],"g")),o=g):h[3]!==void 0&&(o=g):o===g?h[0]===">"?(o=n??C,u=-1):h[1]===void 0?u=-2:(u=o.lastIndex-h[2].length,d=h[1],o=h[3]===void 0?g:h[3]==='"'?de:ce):o===de||o===ce?o=g:o===le||o===ue?o=C:(o=g,n=void 0);const f=o===g&&i[a+1].startsWith("/>")?" ":"";s+=o===C?l+We:u>=0?(r.push(d),l.slice(0,u)+be+l.slice(u)+v+f):l+v+(u===-2?a:f)}return[Ae(i,s+(i[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),r]};class T{constructor({strings:e,_$litType$:t},r){let n;this.parts=[];let s=0,o=0;const a=e.length-1,l=this.parts,[d,h]=Ge(e,t);if(this.el=T.createElement(d,r),b.currentNode=this.el.content,t===2||t===3){const u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(n=b.nextNode())!==null&&l.length<a;){if(n.nodeType===1){if(n.hasAttributes())for(const u of n.getAttributeNames())if(u.endsWith(be)){const m=h[o++],f=n.getAttribute(u).split(v),y=/([.?@])?(.*)/.exec(m);l.push({type:1,index:s,name:y[2],strings:f,ctor:y[1]==="."?Ze:y[1]==="?"?Je:y[1]==="@"?Xe:B}),n.removeAttribute(u)}else u.startsWith(v)&&(l.push({type:6,index:s}),n.removeAttribute(u));if(ye.test(n.tagName)){const u=n.textContent.split(v),m=u.length-1;if(m>0){n.textContent=H?H.emptyScript:"";for(let f=0;f<m;f++)n.append(u[f],P()),b.nextNode(),l.push({type:2,index:++s});n.append(u[m],P())}}}else if(n.nodeType===8)if(n.data===$e)l.push({type:2,index:s});else{let u=-1;for(;(u=n.data.indexOf(v,u+1))!==-1;)l.push({type:7,index:s}),u+=v.length-1}s++}}static createElement(e,t){const r=$.createElement("template");return r.innerHTML=e,r}}function E(i,e,t=i,r){if(e===w)return e;let n=r!==void 0?t._$Co?.[r]:t._$Cl;const s=M(e)?void 0:e._$litDirective$;return n?.constructor!==s&&(n?._$AO?.(!1),s===void 0?n=void 0:(n=new s(i),n._$AT(i,t,r)),r!==void 0?(t._$Co??(t._$Co=[]))[r]=n:t._$Cl=n),n!==void 0&&(e=E(i,n._$AS(i,e.values),n,r)),e}class Ke{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:r}=this._$AD,n=(e?.creationScope??$).importNode(t,!0);b.currentNode=n;let s=b.nextNode(),o=0,a=0,l=r[0];for(;l!==void 0;){if(o===l.index){let d;l.type===2?d=new L(s,s.nextSibling,this,e):l.type===1?d=new l.ctor(s,l.name,l.strings,this,e):l.type===6&&(d=new Ye(s,this,e)),this._$AV.push(d),l=r[++a]}o!==l?.index&&(s=b.nextNode(),o++)}return b.currentNode=$,n}p(e){let t=0;for(const r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(e,r,t),t+=r.strings.length-2):r._$AI(e[t])),t++}}class L{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,r,n){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=r,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=E(this,e,t),M(e)?e===c||e==null||e===""?(this._$AH!==c&&this._$AR(),this._$AH=c):e!==this._$AH&&e!==w&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Qe(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==c&&M(this._$AH)?this._$AA.nextSibling.data=e:this.T($.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:r}=e,n=typeof r=="number"?this._$AC(e):(r.el===void 0&&(r.el=T.createElement(Ae(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===n)this._$AH.p(t);else{const s=new Ke(n,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=he.get(e.strings);return t===void 0&&he.set(e.strings,t=new T(e)),t}k(e){X(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let r,n=0;for(const s of e)n===t.length?t.push(r=new L(this.O(P()),this.O(P()),this,this.options)):r=t[n],r._$AI(s),n++;n<t.length&&(this._$AR(r&&r._$AB.nextSibling,n),t.length=n)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const r=oe(e).nextSibling;oe(e).remove(),e=r}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class B{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,r,n,s){this.type=1,this._$AH=c,this._$AN=void 0,this.element=e,this.name=t,this._$AM=n,this.options=s,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=c}_$AI(e,t=this,r,n){const s=this.strings;let o=!1;if(s===void 0)e=E(this,e,t,0),o=!M(e)||e!==this._$AH&&e!==w,o&&(this._$AH=e);else{const a=e;let l,d;for(e=s[0],l=0;l<s.length-1;l++)d=E(this,a[r+l],t,l),d===w&&(d=this._$AH[l]),o||(o=!M(d)||d!==this._$AH[l]),d===c?e=c:e!==c&&(e+=(d??"")+s[l+1]),this._$AH[l]=d}o&&!n&&this.j(e)}j(e){e===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Ze extends B{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===c?void 0:e}}class Je extends B{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==c)}}class Xe extends B{constructor(e,t,r,n,s){super(e,t,r,n,s),this.type=5}_$AI(e,t=this){if((e=E(this,e,t,0)??c)===w)return;const r=this._$AH,n=e===c&&r!==c||e.capture!==r.capture||e.once!==r.once||e.passive!==r.passive,s=e!==c&&(r===c||n);n&&this.element.removeEventListener(this.name,this,r),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Ye{constructor(e,t,r){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(e){E(this,e)}}const et=I.litHtmlPolyfillSupport;et?.(T,L),(I.litHtmlVersions??(I.litHtmlVersions=[])).push("3.3.3");const tt=(i,e,t)=>{const r=t?.renderBefore??e;let n=r._$litPart$;if(n===void 0){const s=t?.renderBefore??null;r._$litPart$=n=new L(e.insertBefore(P(),s),s,void 0,t??{})}return n._$AI(i),n};const O=globalThis;class k extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=tt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}}k._$litElement$=!0,k.finalized=!0,O.litElementHydrateSupport?.({LitElement:k});const rt=O.litElementPolyfillSupport;rt?.({LitElement:k});(O.litElementVersions??(O.litElementVersions=[])).push("4.2.2");const it=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),nt=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),st={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function S(i){return String(i??"").trim().toLowerCase()}function Se(i){const e=S(i);return e?e.replaceAll("_"," "):""}function ot(i){const e=S(i);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:st[e]??Se(e)}function at(i){switch(i){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return Se(i)}}function lt(i){if(S(i.queueRunState)!=="running")return null;const e=S(i.vacuumState),t=S(i.robotState),r=S(i.taskStatus),n=ot(i.errorCode);if(e==="error")return{phase:"error",label:n??"Error"};if(r==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:n?`Paused (${n})`:"Paused"};if(it.has(t))return{phase:"preparing",label:at(t)};if(e==="returning"&&r==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(nt.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function N(i,e){const t=String(i||"").trim();if(!t.startsWith("vacuum."))return null;const r=t.slice(7);return r?`sensor.${r}_${e}`:null}const ut=10,ct=22,Y={suction_level:{control:"select",suffix:"suction_level",options:["quiet","standard","strong","turbo"],optionIndexToOverrideValue:i=>i},water_volume:{control:"number",suffix:"wetness_level",values:[1,2,3],stateToOverrideValue:i=>{const e=Number(String(i??"").trim());return Number.isFinite(e)?e<=ut?1:e>=ct?3:2:null}}};function dt(i,e){const t=String(i||"").trim();if(!t.startsWith("vacuum."))return null;const r=t.slice(7);if(!r)return null;const n=Y[e];return`${n.control}.${r}_${n.suffix}`}function ht(i,e){const t=Y[i];if(t.control==="number")return t.stateToOverrideValue(e);const r=String(e??"").trim().toLowerCase(),n=t.options.indexOf(r);return n<0?null:t.optionIndexToOverrideValue(n)}function pt(i,e,t){return{domain:"ha_dreame",service:"update_running_override",data:{config_entry_id:i,field:e,value:mt(e,t)}}}function mt(i,e){const t=Y[i];if(t.control==="number"){const o=t.stateToOverrideValue(e),a=o?t.values.indexOf(o):-1,l=a<0?0:(a+1)%t.values.length;return t.values[l]}const r=String(e??"").trim().toLowerCase(),n=t.options.indexOf(r),s=n<0?0:(n+1)%t.options.length;return t.optionIndexToOverrideValue(s)}function z(i){return typeof i=="object"&&i!==null&&!Array.isArray(i)}function ft(i){return String(i??"").trim()}function xe(i){return ft(i).toLowerCase()}function q(i){return typeof i!="number"||!Number.isFinite(i)||i<0?null:Math.trunc(i)}function pe(i){return typeof i=="boolean"?i:null}function Q(i,e){return i.filter(t=>t.status===e).length}function vt(i){if(!z(i))return null;const e=i.item_id,t=i.room_id,r=i.room_name,n=i.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof r!="string"||typeof n!="string"?null:{itemId:e,roomId:t,roomName:r,status:n,overrides:z(i.overrides)?{...i.overrides}:{},result:typeof i.result=="string"?i.result:null}}function we(i){const e=xe(i);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function _t(i){if(!z(i))return[];const e=i.queue_items;return Array.isArray(e)?e.flatMap(t=>{const r=vt(t);return r?[r]:[]}):[]}function gt(i){const e=i?.attributes,t=_t(e),r=z(e)?e:{};return{runState:xe(i?.state)||"unknown",allowRobotCommands:pe(r.allow_robot_commands),autoReconcileEnabled:pe(r.auto_reconcile_enabled),configEntryId:typeof r.config_entry_id=="string"?r.config_entry_id:null,vacuumEntityId:typeof r.vacuum_entity_id=="string"?r.vacuum_entity_id:null,pendingItems:q(r.pending_items)??Q(t,"pending"),runningItems:q(r.running_items)??Q(t,"running"),completedItems:q(r.completed_items)??Q(t,"completed"),totalItems:q(r.total_items)??t.length,items:t}}const Ee={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},Ce={water_volume:2,suction_level:1,repeats:1};function Re(i){if(i==null)return null;if(typeof i=="number")return Number.isFinite(i)?Math.trunc(i):null;if(typeof i=="string"){const e=Number(i.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function Ie(i,e){const t={};for(const[r,n]of Object.entries(e??{}))n!=null&&(t[r]=n);for(const[r,n]of Object.entries(i??{}))n!=null&&(t[r]=n);return t}function bt(i,e,t){const r=Ie(e,t);return Re(r[i])??Ce[i]}function Oe(i,e,t){const r=bt(i,e,t),n=Ee[i].find(s=>s.value===r);return n?n.label:String(r)}function $t(i,e,t){const r=Ie(e,t),n=Ee[i],s=Re(r[i])??Ce[i],o=n.findIndex(l=>l.value===s),a=o<0?0:(o+1)%n.length;return r[i]=n[a].value,r}function me(i){if(typeof i=="number"&&Number.isInteger(i))return i;if(typeof i!="string")return null;const e=i.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function G(i,e){if(Array.isArray(i)){for(const s of i)G(s,e);return}if(typeof i!="object"||i===null)return;const t=i,r=me(t.id),n=typeof t.name=="string"?t.name.trim():"";r!==null&&n&&e.push({roomId:r,roomName:n});for(const[s,o]of Object.entries(t)){const a=me(s);if(a!==null&&typeof o=="string"){const l=o.trim();if(l){e.push({roomId:a,roomName:l});continue}}G(o,e)}}function yt(i){const e=[];G(i,e);const t=new Map;for(const r of e)t.set(r.roomId,r.roomName);return Array.from(t.entries()).map(([r,n])=>({roomId:r,roomName:n})).sort((r,n)=>r.roomId-n.roomId)}const D="ha-dreame-queue-card",At="ha-dreame-queue-card-editor",St="HA Dreame Queue",xt="sensor.ha_dreame_queue_status",wt=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}],Et=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"}];function Ct(i){return Object.entries(i?.states??{}).filter(([e,t])=>e.startsWith("sensor.")&&Ht(t)).map(([e])=>e).sort()}function Rt(i){return{entity:Ct(i)[0]??xt}}function It(i,e){const t=V(e.title)||St,r=V(e.entity)||null;if(!r)return fe({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const n=i?.states[r];if(!n)return fe({title:t,status:"missing",entityId:r,message:"Queue entity not found."});const s=gt(n),o=Ot(i,s),a=Tt(i,s),l=Ut(i,s);return{title:t,status:"ready",entityId:r,message:null,summary:Mt(s,o,a),snapshot:s,activity:o,activeControls:Pt(s,o,a),canClearPending:s.pendingItems>0,rooms:l,rows:kt(i,s)}}function fe({title:i,status:e,entityId:t,message:r}){return{title:i,status:e,entityId:t,message:r,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function Ot(i,e){const t=e.vacuumEntityId;return!i||!t?null:lt({queueRunState:e.runState,vacuumState:x(i,t),robotState:x(i,N(t,"state")),taskStatus:x(i,N(t,"task_status")),errorCode:x(i,N(t,"error"))})}function kt(i,e){const t=e.items,r=Nt(i,e),n=t.flatMap((a,l)=>a.status==="pending"?[l]:[]),s=n[0]??null,o=n[n.length-1]??null;return t.map((a,l)=>({itemId:a.itemId,queuePosition:l,roomName:a.roomName,status:a.status,statusLabel:a.status==="pending"?"Queued":we(a.status),...a.status==="running"&&r!==null?{progress:r}:{},overrides:{...a.overrides},canRemove:a.status==="pending",canMoveUp:a.status==="pending"&&l!==s,canMoveDown:a.status==="pending"&&l!==o,overrideControls:a.status==="pending"?Lt(a.overrides):qt(i,e,a)}))}function Nt(i,e){const t=e.vacuumEntityId;if(!i||!t)return null;const r=N(t,"cleaning_progress"),n=ve(r?i.states[r]?.state:void 0);if(n!==null)return n;const s=i.states[t]?.attributes;return ee(s)?ve(s.cleaning_progress):null}function ve(i){if(i==null)return null;const e=Number(String(i).trim());return Number.isFinite(e)?Math.max(0,Math.min(100,Math.round(e))):null}function Pt(i,e,t){const r=i.allowRobotCommands===!1?{disabled:!0,disabledReason:"Robot commands disabled"}:{};return i.runState==="running"?e?.phase==="paused"||e?.phase==="error"?[{ariaLabel:"Continue robot run",label:"Continue",service:"resume_queue",...r},{ariaLabel:"End robot run",label:"End",service:"cancel_queue",...r}]:[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue",...r},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room",...r}]:i.runState==="idle"&&i.pendingItems>0?[{...(i.allowRobotCommands===!1?{ariaLabel:"Start queue",label:"Start",service:"start_queue"}:t?.control)??{ariaLabel:"Start queue",label:"Start",service:"start_queue"},...r}]:[]}function Mt(i,e,t){if(e)return e.label;if(i.runState==="idle"&&i.pendingItems>0&&t)return t.summary;switch(i.runState){case"idle":return i.pendingItems===1?"Ready to start 1 room.":i.pendingItems>1?`Ready to start ${i.pendingItems} rooms.`:"Queue is empty.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access before restarting.";case"out_of_sync":return"Queue out of sync. Review robot state before restarting.";case"manual_control":return"Manual control active.";default:return`Queue state: ${we(i.runState)}.`}}function Tt(i,e){if(!i||e.runState!=="idle"||e.pendingItems<1)return null;const t=e.vacuumEntityId;if(!t)return null;const r=V(x(i,t)).toLowerCase(),n=V(x(i,N(t,"task_status"))).toLowerCase();return r==="unavailable"||r==="unknown"||n==="unavailable"||n==="unknown"?{control:{ariaLabel:"Start queue",disabled:!0,disabledReason:"Robot is unavailable",label:"Start",service:"start_queue"},summary:"Robot is unavailable. Check its connection before starting."}:n&&n!=="completed"?{control:{ariaLabel:"Start queue",disabled:!0,disabledReason:"Waiting for the previous robot task to finish",label:"Start",service:"start_queue"},summary:r==="returning"?"Robot is returning to base before the queue can start.":"Robot is finishing a previous task before the queue can start."}:null}function Lt(i){return wt.map(e=>({controlType:"pending",field:e.field,label:e.label,valueLabel:Oe(e.field,i,{})}))}function qt(i,e,t){return!i||t.status!=="running"||!e.configEntryId||!e.vacuumEntityId?[]:Et.flatMap(r=>{const n=dt(e.vacuumEntityId??"",r.field);if(!n)return[];const s=i.states[n]?.state;if(s===void 0)return[];const o=ht(r.field,s);if(o===null)return[];const a=pt(e.configEntryId??"",r.field,s);return[{controlType:"running",field:r.field,label:r.label,valueLabel:Oe(r.field,{[r.field]:o},{}),value:a.data.value}]})}function Ut(i,e){const t=e.vacuumEntityId;if(!i||!t)return[];const r=i.states[t]?.attributes;return yt(ee(r)?r.rooms:void 0)}function x(i,e){return e?i.states[e]?.state:void 0}function V(i){return String(i??"").trim()}function ee(i){return typeof i=="object"&&i!==null&&!Array.isArray(i)}function Ht(i){const e=i?.attributes;return ee(e)&&Array.isArray(e.queue_items)&&typeof e.config_entry_id=="string"}const j=class j extends k{constructor(){super(...arguments),this._config={},this._serviceError=null}static async getConfigElement(){return await Pe(()=>import("./ha-dreame-queue-card-editor-lXmQUl9-.js"),[]),document.createElement(At)}static getStubConfig(e){return Rt(e)}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 6}render(){const e=It(this.hass,this._config),t=e.snapshot,r=t?.configEntryId;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="activity-line">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          <div class="header-right">
            ${t?this._renderHeaderActions(e.activeControls,e.canClearPending,r):c}
            ${t?p`<span class="state-pill ${t.runState}"
                  >${this._stateLabel(t.runState)}</span
                >`:c}
          </div>
        </div>

        ${this._serviceError?p`<div class="message service-error">${this._serviceError}</div>`:c}

        ${e.message?p`<div class="message">${e.message}</div>`:p`
              ${e.rooms.length?p`
                    <div class="section-title">Available rooms</div>
                    <div class="room-actions">
                      ${e.rooms.map(n=>p`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!r}
                            @click=${()=>this._addRoom(r,n.roomId,n.roomName)}
                          >
                            <ha-icon icon="mdi:plus"></ha-icon>
                            ${n.roomName}
                          </button>
                        `)}
                    </div>
                  `:c}
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
                              ${this._renderQueueItemActions(n,r)}
                            </div>
                            ${n.overrideControls.length?p`
                                  <div class="item-actions">
                                    <div class="override-controls">
                                      ${n.overrideControls.map(s=>this._renderOverrideControl(n.roomName,n.itemId,n.overrides,s,r))}
                                    </div>
                                  </div>
                                `:c}
                            ${n.progress!==void 0?this._renderProgress(n.progress):c}
                          </div>
                        </div>
                      `):p`<div class="empty">Queue is empty.</div>`}
              </div>
            `}
      </ha-card>
    `}_renderProgress(e){return p`
      <div class="progress">
        <div
          aria-label="Room cleaning progress"
          aria-valuemax="100"
          aria-valuemin="0"
          aria-valuenow=${e}
          class="progress-track"
          role="progressbar"
        >
          <div class="progress-fill" style=${`width: ${e}%;`}></div>
        </div>
        <span class="progress-label">${e}%</span>
      </div>
    `}_renderHeaderActions(e,t,r){return!e.length&&!t?c:p`
      <div class="header-actions">
        ${e.map(n=>p`
            <button
              aria-label=${n.ariaLabel}
              class="icon-btn ${n.service==="cancel_queue"?"delete":""}"
              title=${n.disabledReason??n.ariaLabel}
              type="button"
              ?disabled=${!r||n.disabled===!0}
              @click=${()=>this._callQueueService(r,n.service)}
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
                ?disabled=${!r}
                @click=${()=>this._clearPending(r)}
              >
                <ha-icon icon="mdi:playlist-remove"></ha-icon>
              </button>
            `:c}
      </div>
    `}_renderQueueItemActions(e,t){return!e.canMoveUp&&!e.canMoveDown&&!e.canRemove?c:p`
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
            `:c}
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
            `:c}
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
            `:c}
      </div>
    `}_renderOverrideControl(e,t,r,n,s){return p`
      <button
        aria-label=${`Cycle ${e} ${this._overrideAriaField(n.field)}`}
        class="override-btn"
        title=${`${n.label}: ${n.valueLabel}`}
        type="button"
        ?disabled=${!s}
        @click=${()=>this._cycleOverride(s,t,r,n)}
      >
        <ha-icon icon=${this._overrideIcon(n.field,n.valueLabel)}></ha-icon>
        ${this._renderOverrideValue(n.field,n.valueLabel)}
      </button>
    `}_renderOverrideValue(e,t){if(e==="repeats")return p`<span>${t}</span>`;const r=e==="water_volume"?3:4;return this._renderBars(r,this._overrideActiveBars(e,t))}_renderBars(e,t){const r=Math.max(0,Math.min(e,t));return p`
      <span class="override-bars" aria-hidden="true">
        ${Array.from({length:e},(n,s)=>{const o=6+s*2,a=s<r;return p`
            <span
              class="override-bar ${a?"active":""}"
              style=${`height:${o}px;`}
            ></span>
          `})}
      </span>
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_activeControlIcon(e){return e==="start_queue"||e==="resume_queue"?"mdi:play":e==="skip_current_room"?"mdi:skip-next":"mdi:stop"}_overrideIcon(e,t){return e==="water_volume"?t==="Off"?"mdi:water-off":"mdi:water-percent":e==="suction_level"?t==="Off"?"mdi:fan-off":"mdi:fan":"mdi:repeat"}_overrideActiveBars(e,t){return t==="Off"?0:e==="water_volume"?{Min:1,Med:2,Max:3}[t]??0:e==="suction_level"?{Min:1,Med:2,Max:3,Turbo:4}[t]??0:0}_addRoom(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:r})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:r})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}async _callQueueService(e,t){if(!(!e||!this.hass?.callService)){this._serviceError=null;try{await this.hass.callService("ha_dreame",t,{config_entry_id:e})}catch(r){const n=r instanceof Error?r.message:String(r??"");this._serviceError=n.includes("previous robot task is still active")?"Robot is still finishing a previous task. Try again when it is ready.":"The queue command failed. Check Home Assistant for details."}}}_updateOverrides(e,t,r,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:$t(r,n,{})})}_cycleOverride(e,t,r,n){if(n.controlType==="running"){this._updateRunningOverride(e,n.field,n.value);return}this._updateOverrides(e,t,n.field,r)}_updateRunningOverride(e,t,r){!e||!this.hass?.callService||t==="repeats"||r===void 0||this.hass.callService("ha_dreame","update_running_override",{config_entry_id:e,field:t,value:r})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};j.properties={hass:{attribute:!1},_config:{state:!0},_serviceError:{state:!0}},j.styles=Te`
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

    .progress {
      display: grid;
      gap: 4px;
      margin-top: 2px;
    }

    .progress-track {
      background: color-mix(in srgb, var(--divider-color) 55%, transparent);
      border-radius: 999px;
      height: 7px;
      overflow: hidden;
    }

    .progress-fill {
      background: var(--primary-color, #03a9f4);
      height: 100%;
      transition: width 180ms ease-out;
    }

    .progress-label {
      color: var(--secondary-text-color);
      font-size: 0.76rem;
      line-height: 1.2;
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
  `;let K=j;customElements.get(D)||customElements.define(D,K);window.customCards=window.customCards??[];window.customCards.some(i=>i.type===D)||window.customCards.push({type:D,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});export{At as C,St as D,Te as a,p as b,k as i,Ct as q};
