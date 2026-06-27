const Re="modulepreload",Ie=function(i){return"/"+i},Y={},Ne=function(e,t,r){let n=Promise.resolve();if(t&&t.length>0){let l=function(u){return Promise.all(u.map(h=>Promise.resolve(h).then(c=>({status:"fulfilled",value:c}),c=>({status:"rejected",reason:c}))))};document.getElementsByTagName("link");const o=document.querySelector("meta[property=csp-nonce]"),a=o?.nonce||o?.getAttribute("nonce");n=l(t.map(u=>{if(u=Ie(u),u in Y)return;Y[u]=!0;const h=u.endsWith(".css"),c=h?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${u}"]${c}`))return;const m=document.createElement("link");if(m.rel=h?"stylesheet":Re,h||(m.as="script"),m.crossOrigin="",m.href=u,a&&m.setAttribute("nonce",a),document.head.appendChild(m),h)return new Promise((f,y)=>{m.addEventListener("load",f),m.addEventListener("error",()=>y(new Error(`Unable to preload CSS for ${u}`)))})}))}function s(o){const a=new Event("vite:preloadError",{cancelable:!0});if(a.payload=o,window.dispatchEvent(a),!a.defaultPrevented)throw o}return n.then(o=>{for(const a of o||[])a.status==="rejected"&&s(a.reason);return e().catch(s)})};const U=globalThis,K=U.ShadowRoot&&(U.ShadyCSS===void 0||U.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),ee=new WeakMap;let fe=class{constructor(e,t,r){if(this._$cssResult$=!0,r!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(K&&e===void 0){const r=t!==void 0&&t.length===1;r&&(e=ee.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),r&&ee.set(t,e))}return e}toString(){return this.cssText}};const Me=i=>new fe(typeof i=="string"?i:i+"",void 0,Z),Pe=(i,...e)=>{const t=i.length===1?i[0]:e.reduce((r,n,s)=>r+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+i[s+1],i[0]);return new fe(t,i,Z)},ke=(i,e)=>{if(K)i.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const r=document.createElement("style"),n=U.litNonce;n!==void 0&&r.setAttribute("nonce",n),r.textContent=t.cssText,i.appendChild(r)}},te=K?i=>i:i=>i instanceof CSSStyleSheet?(e=>{let t="";for(const r of e.cssRules)t+=r.cssText;return Me(t)})(i):i;const{is:Te,defineProperty:Le,getOwnPropertyDescriptor:Ue,getOwnPropertyNames:qe,getOwnPropertySymbols:He,getPrototypeOf:De}=Object,v=globalThis,re=v.trustedTypes,ze=re?re.emptyScript:"",Ve=v.reactiveElementPolyfillSupport,C=(i,e)=>i,Q={toAttribute(i,e){switch(e){case Boolean:i=i?ze:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,e){let t=i;switch(e){case Boolean:t=i!==null;break;case Number:t=i===null?null:Number(i);break;case Object:case Array:try{t=JSON.parse(i)}catch{t=null}}return t}},_e=(i,e)=>!Te(i,e),ie={attribute:!0,type:String,converter:Q,reflect:!1,useDefault:!1,hasChanged:_e};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),v.litPropertyMetadata??(v.litPropertyMetadata=new WeakMap);let A=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=ie){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const r=Symbol(),n=this.getPropertyDescriptor(e,r,t);n!==void 0&&Le(this.prototype,e,n)}}static getPropertyDescriptor(e,t,r){const{get:n,set:s}=Ue(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:n,set(o){const a=n?.call(this);s?.call(this,o),this.requestUpdate(e,a,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??ie}static _$Ei(){if(this.hasOwnProperty(C("elementProperties")))return;const e=De(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(C("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(C("properties"))){const t=this.properties,r=[...qe(t),...He(t)];for(const n of r)this.createProperty(n,t[n])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[r,n]of t)this.elementProperties.set(r,n)}this._$Eh=new Map;for(const[t,r]of this.elementProperties){const n=this._$Eu(t,r);n!==void 0&&this._$Eh.set(n,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const r=new Set(e.flat(1/0).reverse());for(const n of r)t.unshift(te(n))}else e!==void 0&&t.push(te(e));return t}static _$Eu(e,t){const r=t.attribute;return r===!1?void 0:typeof r=="string"?r:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const r of t.keys())this.hasOwnProperty(r)&&(e.set(r,this[r]),delete this[r]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ke(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,r){this._$AK(e,r)}_$ET(e,t){const r=this.constructor.elementProperties.get(e),n=this.constructor._$Eu(e,r);if(n!==void 0&&r.reflect===!0){const s=(r.converter?.toAttribute!==void 0?r.converter:Q).toAttribute(t,r.type);this._$Em=e,s==null?this.removeAttribute(n):this.setAttribute(n,s),this._$Em=null}}_$AK(e,t){const r=this.constructor,n=r._$Eh.get(e);if(n!==void 0&&this._$Em!==n){const s=r.getPropertyOptions(n),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:Q;this._$Em=n;const a=o.fromAttribute(t,s.type);this[n]=a??this._$Ej?.get(n)??a,this._$Em=null}}requestUpdate(e,t,r,n=!1,s){if(e!==void 0){const o=this.constructor;if(n===!1&&(s=this[e]),r??(r=o.getPropertyOptions(e)),!((r.hasChanged??_e)(s,t)||r.useDefault&&r.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,r))))return;this.C(e,t,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:r,reflect:n,wrapped:s},o){r&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||r||(t=void 0),this._$AL.set(e,t)),n===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[n,s]of this._$Ep)this[n]=s;this._$Ep=void 0}const r=this.constructor.elementProperties;if(r.size>0)for(const[n,s]of r){const{wrapped:o}=s,a=this[n];o!==!0||this._$AL.has(n)||a===void 0||this.C(n,void 0,s,a)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(t)):this._$EM()}catch(r){throw e=!1,this._$EM(),r}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[C("elementProperties")]=new Map,A[C("finalized")]=new Map,Ve?.({ReactiveElement:A}),(v.reactiveElementVersions??(v.reactiveElementVersions=[])).push("2.1.2");const O=globalThis,ne=i=>i,q=O.trustedTypes,se=q?q.createPolicy("lit-html",{createHTML:i=>i}):void 0,ve="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,ge="?"+_,je=`<${ge}>`,$=document,N=()=>$.createComment(""),M=i=>i===null||typeof i!="object"&&typeof i!="function",J=Array.isArray,Be=i=>J(i)||typeof i?.[Symbol.iterator]=="function",j=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,oe=/-->/g,ae=/>/g,g=RegExp(`>|${j}(?:([^\\s"'>=/]+)(${j}*=${j}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),le=/'/g,ce=/"/g,be=/^(?:script|style|textarea|title)$/i,We=i=>(e,...t)=>({_$litType$:i,strings:e,values:t}),p=We(1),w=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),ue=new WeakMap,b=$.createTreeWalker($,129);function $e(i,e){if(!J(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return se!==void 0?se.createHTML(e):e}const Qe=(i,e)=>{const t=i.length-1,r=[];let n,s=e===2?"<svg>":e===3?"<math>":"",o=E;for(let a=0;a<t;a++){const l=i[a];let u,h,c=-1,m=0;for(;m<l.length&&(o.lastIndex=m,h=o.exec(l),h!==null);)m=o.lastIndex,o===E?h[1]==="!--"?o=oe:h[1]!==void 0?o=ae:h[2]!==void 0?(be.test(h[2])&&(n=RegExp("</"+h[2],"g")),o=g):h[3]!==void 0&&(o=g):o===g?h[0]===">"?(o=n??E,c=-1):h[1]===void 0?c=-2:(c=o.lastIndex-h[2].length,u=h[1],o=h[3]===void 0?g:h[3]==='"'?ce:le):o===ce||o===le?o=g:o===oe||o===ae?o=E:(o=g,n=void 0);const f=o===g&&i[a+1].startsWith("/>")?" ":"";s+=o===E?l+je:c>=0?(r.push(u),l.slice(0,c)+ve+l.slice(c)+_+f):l+_+(c===-2?a:f)}return[$e(i,s+(i[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),r]};class P{constructor({strings:e,_$litType$:t},r){let n;this.parts=[];let s=0,o=0;const a=e.length-1,l=this.parts,[u,h]=Qe(e,t);if(this.el=P.createElement(u,r),b.currentNode=this.el.content,t===2||t===3){const c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(n=b.nextNode())!==null&&l.length<a;){if(n.nodeType===1){if(n.hasAttributes())for(const c of n.getAttributeNames())if(c.endsWith(ve)){const m=h[o++],f=n.getAttribute(c).split(_),y=/([.?@])?(.*)/.exec(m);l.push({type:1,index:s,name:y[2],strings:f,ctor:y[1]==="."?Ge:y[1]==="?"?Ke:y[1]==="@"?Ze:V}),n.removeAttribute(c)}else c.startsWith(_)&&(l.push({type:6,index:s}),n.removeAttribute(c));if(be.test(n.tagName)){const c=n.textContent.split(_),m=c.length-1;if(m>0){n.textContent=q?q.emptyScript:"";for(let f=0;f<m;f++)n.append(c[f],N()),b.nextNode(),l.push({type:2,index:++s});n.append(c[m],N())}}}else if(n.nodeType===8)if(n.data===ge)l.push({type:2,index:s});else{let c=-1;for(;(c=n.data.indexOf(_,c+1))!==-1;)l.push({type:7,index:s}),c+=_.length-1}s++}}static createElement(e,t){const r=$.createElement("template");return r.innerHTML=e,r}}function S(i,e,t=i,r){if(e===w)return e;let n=r!==void 0?t._$Co?.[r]:t._$Cl;const s=M(e)?void 0:e._$litDirective$;return n?.constructor!==s&&(n?._$AO?.(!1),s===void 0?n=void 0:(n=new s(i),n._$AT(i,t,r)),r!==void 0?(t._$Co??(t._$Co=[]))[r]=n:t._$Cl=n),n!==void 0&&(e=S(i,n._$AS(i,e.values),n,r)),e}class Fe{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:r}=this._$AD,n=(e?.creationScope??$).importNode(t,!0);b.currentNode=n;let s=b.nextNode(),o=0,a=0,l=r[0];for(;l!==void 0;){if(o===l.index){let u;l.type===2?u=new k(s,s.nextSibling,this,e):l.type===1?u=new l.ctor(s,l.name,l.strings,this,e):l.type===6&&(u=new Je(s,this,e)),this._$AV.push(u),l=r[++a]}o!==l?.index&&(s=b.nextNode(),o++)}return b.currentNode=$,n}p(e){let t=0;for(const r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(e,r,t),t+=r.strings.length-2):r._$AI(e[t])),t++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,r,n){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=r,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=S(this,e,t),M(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==w&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Be(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&M(this._$AH)?this._$AA.nextSibling.data=e:this.T($.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:r}=e,n=typeof r=="number"?this._$AC(e):(r.el===void 0&&(r.el=P.createElement($e(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===n)this._$AH.p(t);else{const s=new Fe(n,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=ue.get(e.strings);return t===void 0&&ue.set(e.strings,t=new P(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let r,n=0;for(const s of e)n===t.length?t.push(r=new k(this.O(N()),this.O(N()),this,this.options)):r=t[n],r._$AI(s),n++;n<t.length&&(this._$AR(r&&r._$AB.nextSibling,n),t.length=n)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const r=ne(e).nextSibling;ne(e).remove(),e=r}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class V{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,r,n,s){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=n,this.options=s,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=d}_$AI(e,t=this,r,n){const s=this.strings;let o=!1;if(s===void 0)e=S(this,e,t,0),o=!M(e)||e!==this._$AH&&e!==w,o&&(this._$AH=e);else{const a=e;let l,u;for(e=s[0],l=0;l<s.length-1;l++)u=S(this,a[r+l],t,l),u===w&&(u=this._$AH[l]),o||(o=!M(u)||u!==this._$AH[l]),u===d?e=d:e!==d&&(e+=(u??"")+s[l+1]),this._$AH[l]=u}o&&!n&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Ge extends V{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}}class Ke extends V{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}}class Ze extends V{constructor(e,t,r,n,s){super(e,t,r,n,s),this.type=5}_$AI(e,t=this){if((e=S(this,e,t,0)??d)===w)return;const r=this._$AH,n=e===d&&r!==d||e.capture!==r.capture||e.once!==r.once||e.passive!==r.passive,s=e!==d&&(r===d||n);n&&this.element.removeEventListener(this.name,this,r),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Je{constructor(e,t,r){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(e){S(this,e)}}const Xe=O.litHtmlPolyfillSupport;Xe?.(P,k),(O.litHtmlVersions??(O.litHtmlVersions=[])).push("3.3.3");const Ye=(i,e,t)=>{const r=t?.renderBefore??e;let n=r._$litPart$;if(n===void 0){const s=t?.renderBefore??null;r._$litPart$=n=new k(e.insertBefore(N(),s),s,void 0,t??{})}return n._$AI(i),n};const R=globalThis;class I extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ye(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}}I._$litElement$=!0,I.finalized=!0,R.litElementHydrateSupport?.({LitElement:I});const et=R.litElementPolyfillSupport;et?.({LitElement:I});(R.litElementVersions??(R.litElementVersions=[])).push("4.2.2");const tt=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),rt=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),it={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function x(i){return String(i??"").trim().toLowerCase()}function ye(i){const e=x(i);return e?e.replaceAll("_"," "):""}function nt(i){const e=x(i);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:it[e]??ye(e)}function st(i){switch(i){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return ye(i)}}function ot(i){if(x(i.queueRunState)!=="running")return null;const e=x(i.vacuumState),t=x(i.robotState),r=x(i.taskStatus),n=nt(i.errorCode);if(e==="error")return{phase:"error",label:n??"Error"};if(r==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:n?`Paused (${n})`:"Paused"};if(tt.has(t))return{phase:"preparing",label:st(t)};if(e==="returning"&&r==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(rt.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function B(i,e){const t=String(i||"").trim();if(!t.startsWith("vacuum."))return null;const r=t.slice(7);return r?`sensor.${r}_${e}`:null}const at=10,lt=22,X={suction_level:{control:"select",suffix:"suction_level",options:["quiet","standard","strong","turbo"],optionIndexToOverrideValue:i=>i},water_volume:{control:"number",suffix:"wetness_level",values:[1,2,3],stateToOverrideValue:i=>{const e=Number(String(i??"").trim());return Number.isFinite(e)?e<=at?1:e>=lt?3:2:null}}};function ct(i,e){const t=String(i||"").trim();if(!t.startsWith("vacuum."))return null;const r=t.slice(7);if(!r)return null;const n=X[e];return`${n.control}.${r}_${n.suffix}`}function ut(i,e){const t=X[i];if(t.control==="number")return t.stateToOverrideValue(e);const r=String(e??"").trim().toLowerCase(),n=t.options.indexOf(r);return n<0?null:t.optionIndexToOverrideValue(n)}function dt(i,e,t){return{domain:"ha_dreame",service:"update_running_override",data:{config_entry_id:i,field:e,value:ht(e,t)}}}function ht(i,e){const t=X[i];if(t.control==="number"){const o=t.stateToOverrideValue(e),a=o?t.values.indexOf(o):-1,l=a<0?0:(a+1)%t.values.length;return t.values[l]}const r=String(e??"").trim().toLowerCase(),n=t.options.indexOf(r),s=n<0?0:(n+1)%t.options.length;return t.optionIndexToOverrideValue(s)}function H(i){return typeof i=="object"&&i!==null&&!Array.isArray(i)}function pt(i){return String(i??"").trim()}function Ae(i){return pt(i).toLowerCase()}function T(i){return typeof i!="number"||!Number.isFinite(i)||i<0?null:Math.trunc(i)}function de(i){return typeof i=="boolean"?i:null}function W(i,e){return i.filter(t=>t.status===e).length}function mt(i){if(!H(i))return null;const e=i.item_id,t=i.room_id,r=i.room_name,n=i.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof r!="string"||typeof n!="string"?null:{itemId:e,roomId:t,roomName:r,status:n,overrides:H(i.overrides)?{...i.overrides}:{},result:typeof i.result=="string"?i.result:null}}function xe(i){const e=Ae(i);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function ft(i){if(!H(i))return[];const e=i.queue_items;return Array.isArray(e)?e.flatMap(t=>{const r=mt(t);return r?[r]:[]}):[]}function _t(i){const e=i?.attributes,t=ft(e),r=H(e)?e:{};return{runState:Ae(i?.state)||"unknown",allowRobotCommands:de(r.allow_robot_commands),autoReconcileEnabled:de(r.auto_reconcile_enabled),configEntryId:typeof r.config_entry_id=="string"?r.config_entry_id:null,vacuumEntityId:typeof r.vacuum_entity_id=="string"?r.vacuum_entity_id:null,pendingItems:T(r.pending_items)??W(t,"pending"),runningItems:T(r.running_items)??W(t,"running"),completedItems:T(r.completed_items)??W(t,"completed"),totalItems:T(r.total_items)??t.length,items:t}}const we={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},vt={water_volume:2,suction_level:1,repeats:1};function Se(i){if(i==null)return null;if(typeof i=="number")return Number.isFinite(i)?Math.trunc(i):null;if(typeof i=="string"){const e=Number(i.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function Ee(i,e){const t={};for(const[r,n]of Object.entries(e??{}))n!=null&&(t[r]=n);for(const[r,n]of Object.entries(i??{}))n!=null&&(t[r]=n);return t}function gt(i,e,t){const r=Ee(e,t);return Se(r[i])??vt[i]}function Ce(i,e,t){const r=gt(i,e,t),n=we[i].find(s=>s.value===r);return n?n.label:String(r)}function bt(i,e,t){const r=Ee(e,t),n=we[i],s=Se(r[i]),o=n.findIndex(l=>l.value===s),a=o<0?0:(o+1)%n.length;return r[i]=n[a].value,r}function he(i){if(typeof i=="number"&&Number.isInteger(i))return i;if(typeof i!="string")return null;const e=i.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function F(i,e){if(Array.isArray(i)){for(const s of i)F(s,e);return}if(typeof i!="object"||i===null)return;const t=i,r=he(t.id),n=typeof t.name=="string"?t.name.trim():"";r!==null&&n&&e.push({roomId:r,roomName:n});for(const[s,o]of Object.entries(t)){const a=he(s);if(a!==null&&typeof o=="string"){const l=o.trim();if(l){e.push({roomId:a,roomName:l});continue}}F(o,e)}}function $t(i){const e=[];F(i,e);const t=new Map;for(const r of e)t.set(r.roomId,r.roomName);return Array.from(t.entries()).map(([r,n])=>({roomId:r,roomName:n})).sort((r,n)=>r.roomId-n.roomId)}const D="ha-dreame-queue-card",yt="ha-dreame-queue-card-editor",At="HA Dreame Queue",xt="sensor.ha_dreame_queue_status",wt=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}],St=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"}];function Et(i){return Object.entries(i?.states??{}).filter(([e,t])=>e.startsWith("sensor.")&&Lt(t)).map(([e])=>e).sort()}function Ct(i){return{entity:Et(i)[0]??xt}}function Ot(i,e){const t=me(e.title)||At,r=me(e.entity)||null;if(!r)return pe({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const n=i?.states[r];if(!n)return pe({title:t,status:"missing",entityId:r,message:"Queue entity not found."});const s=_t(n),o=Rt(i,s),a=Tt(i,s);return{title:t,status:"ready",entityId:r,message:null,summary:Mt(s,o),snapshot:s,activity:o,activeControls:Nt(s,o),canClearPending:s.pendingItems>0,rooms:a,rows:It(i,s)}}function pe({title:i,status:e,entityId:t,message:r}){return{title:i,status:e,entityId:t,message:r,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function Rt(i,e){const t=e.vacuumEntityId;return!i||!t?null:ot({queueRunState:e.runState,vacuumState:L(i,t),robotState:L(i,B(t,"state")),taskStatus:L(i,B(t,"task_status")),errorCode:L(i,B(t,"error"))})}function It(i,e){const t=e.items,r=t.flatMap((o,a)=>o.status==="pending"?[a]:[]),n=r[0]??null,s=r[r.length-1]??null;return t.map((o,a)=>({itemId:o.itemId,queuePosition:a,roomName:o.roomName,status:o.status,statusLabel:xe(o.status),overrides:{...o.overrides},canRemove:o.status==="pending",canMoveUp:o.status==="pending"&&a!==n,canMoveDown:o.status==="pending"&&a!==s,overrideControls:o.status==="pending"?Pt(o.overrides):kt(i,e,o)}))}function Nt(i,e){const t=i.allowRobotCommands===!1?{disabled:!0,disabledReason:"Robot commands disabled"}:{};return i.runState==="running"?e?.phase==="paused"||e?.phase==="error"?[{ariaLabel:"Continue robot run",label:"Continue",service:"resume_queue",...t},{ariaLabel:"End robot run",label:"End",service:"cancel_queue",...t}]:[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue",...t},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room",...t}]:i.runState==="idle"&&i.pendingItems>0?[{ariaLabel:"Start queue",label:"Start",service:"start_queue",...t}]:[]}function Mt(i,e){if(e)return e.label;switch(i.runState){case"idle":return i.pendingItems===1?"Ready to start 1 room.":i.pendingItems>1?`Ready to start ${i.pendingItems} rooms.`:"Queue is empty.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access before restarting.";case"out_of_sync":return"Queue out of sync. Review robot state before restarting.";case"manual_control":return"Manual control active.";default:return`Queue state: ${xe(i.runState)}.`}}function Pt(i){return wt.map(e=>({controlType:"pending",field:e.field,label:e.label,valueLabel:Ce(e.field,i,{})}))}function kt(i,e,t){return!i||t.status!=="running"||!e.configEntryId||!e.vacuumEntityId?[]:St.flatMap(r=>{const n=ct(e.vacuumEntityId??"",r.field);if(!n)return[];const s=i.states[n]?.state;if(s===void 0)return[];const o=ut(r.field,s);if(o===null)return[];const a=dt(e.configEntryId??"",r.field,s);return[{controlType:"running",field:r.field,label:r.label,valueLabel:Ce(r.field,{[r.field]:o},{}),value:a.data.value}]})}function Tt(i,e){const t=e.vacuumEntityId;if(!i||!t)return[];const r=i.states[t]?.attributes;return $t(Oe(r)?r.rooms:void 0)}function L(i,e){return e?i.states[e]?.state:void 0}function me(i){return String(i??"").trim()}function Oe(i){return typeof i=="object"&&i!==null&&!Array.isArray(i)}function Lt(i){const e=i?.attributes;return Oe(e)&&Array.isArray(e.queue_items)&&typeof e.config_entry_id=="string"}const z=class z extends I{constructor(){super(...arguments),this._config={}}static async getConfigElement(){return await Ne(()=>import("./ha-dreame-queue-card-editor-lXmQUl9-.js"),[]),document.createElement(yt)}static getStubConfig(e){return Ct(e)}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 6}render(){const e=Ot(this.hass,this._config),t=e.snapshot,r=t?.configEntryId;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="activity-line">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          <div class="header-right">
            ${t?this._renderHeaderActions(e.activeControls,e.canClearPending,r):d}
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
                            ?disabled=${!r}
                            @click=${()=>this._addRoom(r,n.roomId,n.roomName)}
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
                              ${this._renderQueueItemActions(n,r)}
                            </div>
                            ${n.overrideControls.length?p`
                                  <div class="item-actions">
                                    <div class="override-controls">
                                      ${n.overrideControls.map(s=>this._renderOverrideControl(n.roomName,n.itemId,n.overrides,s,r))}
                                    </div>
                                  </div>
                                `:d}
                          </div>
                        </div>
                      `):p`<div class="empty">Queue is empty.</div>`}
              </div>
            `}
      </ha-card>
    `}_renderHeaderActions(e,t,r){return!e.length&&!t?d:p`
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
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_activeControlIcon(e){return e==="start_queue"||e==="resume_queue"?"mdi:play":e==="skip_current_room"?"mdi:skip-next":"mdi:stop"}_overrideIcon(e,t){return e==="water_volume"?t==="Off"?"mdi:water-off":"mdi:water-percent":e==="suction_level"?t==="Off"?"mdi:fan-off":"mdi:fan":"mdi:repeat"}_overrideActiveBars(e,t){return t==="Off"?0:e==="water_volume"?{Min:1,Med:2,Max:3}[t]??0:e==="suction_level"?{Min:1,Med:2,Max:3,Turbo:4}[t]??0:0}_addRoom(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:r})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:r})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}_callQueueService(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame",t,{config_entry_id:e})}_updateOverrides(e,t,r,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:bt(r,n,{})})}_cycleOverride(e,t,r,n){if(n.controlType==="running"){this._updateRunningOverride(e,n.field,n.value);return}this._updateOverrides(e,t,n.field,r)}_updateRunningOverride(e,t,r){!e||!this.hass?.callService||t==="repeats"||r===void 0||this.hass.callService("ha_dreame","update_running_override",{config_entry_id:e,field:t,value:r})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};z.properties={hass:{attribute:!1},_config:{state:!0}},z.styles=Pe`
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
  `;let G=z;customElements.get(D)||customElements.define(D,G);window.customCards=window.customCards??[];window.customCards.some(i=>i.type===D)||window.customCards.push({type:D,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});export{yt as C,At as D,Pe as a,p as b,I as i,Et as q};
