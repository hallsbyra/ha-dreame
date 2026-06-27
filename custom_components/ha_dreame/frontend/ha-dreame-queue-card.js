const Oe="modulepreload",Ne=function(r){return"/"+r},ee={},Pe=function(e,t,n){let i=Promise.resolve();if(t&&t.length>0){let l=function(c){return Promise.all(c.map(h=>Promise.resolve(h).then(u=>({status:"fulfilled",value:u}),u=>({status:"rejected",reason:u}))))};document.getElementsByTagName("link");const o=document.querySelector("meta[property=csp-nonce]"),a=o?.nonce||o?.getAttribute("nonce");i=l(t.map(c=>{if(c=Ne(c),c in ee)return;ee[c]=!0;const h=c.endsWith(".css"),u=h?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${c}"]${u}`))return;const m=document.createElement("link");if(m.rel=h?"stylesheet":Oe,h||(m.as="script"),m.crossOrigin="",m.href=c,a&&m.setAttribute("nonce",a),document.head.appendChild(m),h)return new Promise((f,y)=>{m.addEventListener("load",f),m.addEventListener("error",()=>y(new Error(`Unable to preload CSS for ${c}`)))})}))}function s(o){const a=new Event("vite:preloadError",{cancelable:!0});if(a.payload=o,window.dispatchEvent(a),!a.defaultPrevented)throw o}return i.then(o=>{for(const a of o||[])a.status==="rejected"&&s(a.reason);return e().catch(s)})};const U=globalThis,K=U.ShadowRoot&&(U.ShadyCSS===void 0||U.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),te=new WeakMap;let _e=class{constructor(e,t,n){if(this._$cssResult$=!0,n!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(K&&e===void 0){const n=t!==void 0&&t.length===1;n&&(e=te.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),n&&te.set(t,e))}return e}toString(){return this.cssText}};const Me=r=>new _e(typeof r=="string"?r:r+"",void 0,Z),ke=(r,...e)=>{const t=r.length===1?r[0]:e.reduce((n,i,s)=>n+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[s+1],r[0]);return new _e(t,r,Z)},Te=(r,e)=>{if(K)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const n=document.createElement("style"),i=U.litNonce;i!==void 0&&n.setAttribute("nonce",i),n.textContent=t.cssText,r.appendChild(n)}},re=K?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(const n of e.cssRules)t+=n.cssText;return Me(t)})(r):r;const{is:Le,defineProperty:Ue,getOwnPropertyDescriptor:qe,getOwnPropertyNames:He,getOwnPropertySymbols:ze,getPrototypeOf:De}=Object,_=globalThis,ne=_.trustedTypes,Ve=ne?ne.emptyScript:"",je=_.reactiveElementPolyfillSupport,C=(r,e)=>r,F={toAttribute(r,e){switch(e){case Boolean:r=r?Ve:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},ge=(r,e)=>!Le(r,e),ie={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:ge};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),_.litPropertyMetadata??(_.litPropertyMetadata=new WeakMap);let A=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=ie){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const n=Symbol(),i=this.getPropertyDescriptor(e,n,t);i!==void 0&&Ue(this.prototype,e,i)}}static getPropertyDescriptor(e,t,n){const{get:i,set:s}=qe(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){const a=i?.call(this);s?.call(this,o),this.requestUpdate(e,a,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??ie}static _$Ei(){if(this.hasOwnProperty(C("elementProperties")))return;const e=De(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(C("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(C("properties"))){const t=this.properties,n=[...He(t),...ze(t)];for(const i of n)this.createProperty(i,t[i])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[n,i]of t)this.elementProperties.set(n,i)}this._$Eh=new Map;for(const[t,n]of this.elementProperties){const i=this._$Eu(t,n);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const n=new Set(e.flat(1/0).reverse());for(const i of n)t.unshift(re(i))}else e!==void 0&&t.push(re(e));return t}static _$Eu(e,t){const n=t.attribute;return n===!1?void 0:typeof n=="string"?n:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const n of t.keys())this.hasOwnProperty(n)&&(e.set(n,this[n]),delete this[n]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Te(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,n){this._$AK(e,n)}_$ET(e,t){const n=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,n);if(i!==void 0&&n.reflect===!0){const s=(n.converter?.toAttribute!==void 0?n.converter:F).toAttribute(t,n.type);this._$Em=e,s==null?this.removeAttribute(i):this.setAttribute(i,s),this._$Em=null}}_$AK(e,t){const n=this.constructor,i=n._$Eh.get(e);if(i!==void 0&&this._$Em!==i){const s=n.getPropertyOptions(i),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:F;this._$Em=i;const a=o.fromAttribute(t,s.type);this[i]=a??this._$Ej?.get(i)??a,this._$Em=null}}requestUpdate(e,t,n,i=!1,s){if(e!==void 0){const o=this.constructor;if(i===!1&&(s=this[e]),n??(n=o.getPropertyOptions(e)),!((n.hasChanged??ge)(s,t)||n.useDefault&&n.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,n))))return;this.C(e,t,n)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:n,reflect:i,wrapped:s},o){n&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||n||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[i,s]of this._$Ep)this[i]=s;this._$Ep=void 0}const n=this.constructor.elementProperties;if(n.size>0)for(const[i,s]of n){const{wrapped:o}=s,a=this[i];o!==!0||this._$AL.has(i)||a===void 0||this.C(i,void 0,s,a)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(n=>n.hostUpdate?.()),this.update(t)):this._$EM()}catch(n){throw e=!1,this._$EM(),n}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[C("elementProperties")]=new Map,A[C("finalized")]=new Map,je?.({ReactiveElement:A}),(_.reactiveElementVersions??(_.reactiveElementVersions=[])).push("2.1.2");const R=globalThis,se=r=>r,H=R.trustedTypes,oe=H?H.createPolicy("lit-html",{createHTML:r=>r}):void 0,be="$lit$",v=`lit$${Math.random().toFixed(9).slice(2)}$`,$e="?"+v,Be=`<${$e}>`,$=document,N=()=>$.createComment(""),P=r=>r===null||typeof r!="object"&&typeof r!="function",J=Array.isArray,We=r=>J(r)||typeof r?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ae=/-->/g,le=/>/g,g=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ue=/'/g,ce=/"/g,ye=/^(?:script|style|textarea|title)$/i,Fe=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),p=Fe(1),w=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),de=new WeakMap,b=$.createTreeWalker($,129);function Ae(r,e){if(!J(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return oe!==void 0?oe.createHTML(e):e}const Qe=(r,e)=>{const t=r.length-1,n=[];let i,s=e===2?"<svg>":e===3?"<math>":"",o=E;for(let a=0;a<t;a++){const l=r[a];let c,h,u=-1,m=0;for(;m<l.length&&(o.lastIndex=m,h=o.exec(l),h!==null);)m=o.lastIndex,o===E?h[1]==="!--"?o=ae:h[1]!==void 0?o=le:h[2]!==void 0?(ye.test(h[2])&&(i=RegExp("</"+h[2],"g")),o=g):h[3]!==void 0&&(o=g):o===g?h[0]===">"?(o=i??E,u=-1):h[1]===void 0?u=-2:(u=o.lastIndex-h[2].length,c=h[1],o=h[3]===void 0?g:h[3]==='"'?ce:ue):o===ce||o===ue?o=g:o===ae||o===le?o=E:(o=g,i=void 0);const f=o===g&&r[a+1].startsWith("/>")?" ":"";s+=o===E?l+Be:u>=0?(n.push(c),l.slice(0,u)+be+l.slice(u)+v+f):l+v+(u===-2?a:f)}return[Ae(r,s+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),n]};class M{constructor({strings:e,_$litType$:t},n){let i;this.parts=[];let s=0,o=0;const a=e.length-1,l=this.parts,[c,h]=Qe(e,t);if(this.el=M.createElement(c,n),b.currentNode=this.el.content,t===2||t===3){const u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(i=b.nextNode())!==null&&l.length<a;){if(i.nodeType===1){if(i.hasAttributes())for(const u of i.getAttributeNames())if(u.endsWith(be)){const m=h[o++],f=i.getAttribute(u).split(v),y=/([.?@])?(.*)/.exec(m);l.push({type:1,index:s,name:y[2],strings:f,ctor:y[1]==="."?Ke:y[1]==="?"?Ze:y[1]==="@"?Je:j}),i.removeAttribute(u)}else u.startsWith(v)&&(l.push({type:6,index:s}),i.removeAttribute(u));if(ye.test(i.tagName)){const u=i.textContent.split(v),m=u.length-1;if(m>0){i.textContent=H?H.emptyScript:"";for(let f=0;f<m;f++)i.append(u[f],N()),b.nextNode(),l.push({type:2,index:++s});i.append(u[m],N())}}}else if(i.nodeType===8)if(i.data===$e)l.push({type:2,index:s});else{let u=-1;for(;(u=i.data.indexOf(v,u+1))!==-1;)l.push({type:7,index:s}),u+=v.length-1}s++}}static createElement(e,t){const n=$.createElement("template");return n.innerHTML=e,n}}function S(r,e,t=r,n){if(e===w)return e;let i=n!==void 0?t._$Co?.[n]:t._$Cl;const s=P(e)?void 0:e._$litDirective$;return i?.constructor!==s&&(i?._$AO?.(!1),s===void 0?i=void 0:(i=new s(r),i._$AT(r,t,n)),n!==void 0?(t._$Co??(t._$Co=[]))[n]=i:t._$Cl=i),i!==void 0&&(e=S(r,i._$AS(r,e.values),i,n)),e}class Ge{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:n}=this._$AD,i=(e?.creationScope??$).importNode(t,!0);b.currentNode=i;let s=b.nextNode(),o=0,a=0,l=n[0];for(;l!==void 0;){if(o===l.index){let c;l.type===2?c=new k(s,s.nextSibling,this,e):l.type===1?c=new l.ctor(s,l.name,l.strings,this,e):l.type===6&&(c=new Xe(s,this,e)),this._$AV.push(c),l=n[++a]}o!==l?.index&&(s=b.nextNode(),o++)}return b.currentNode=$,i}p(e){let t=0;for(const n of this._$AV)n!==void 0&&(n.strings!==void 0?(n._$AI(e,n,t),t+=n.strings.length-2):n._$AI(e[t])),t++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,n,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=n,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=S(this,e,t),P(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==w&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):We(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&P(this._$AH)?this._$AA.nextSibling.data=e:this.T($.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:n}=e,i=typeof n=="number"?this._$AC(e):(n.el===void 0&&(n.el=M.createElement(Ae(n.h,n.h[0]),this.options)),n);if(this._$AH?._$AD===i)this._$AH.p(t);else{const s=new Ge(i,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=de.get(e.strings);return t===void 0&&de.set(e.strings,t=new M(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let n,i=0;for(const s of e)i===t.length?t.push(n=new k(this.O(N()),this.O(N()),this,this.options)):n=t[i],n._$AI(s),i++;i<t.length&&(this._$AR(n&&n._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const n=se(e).nextSibling;se(e).remove(),e=n}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class j{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,n,i,s){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=s,n.length>2||n[0]!==""||n[1]!==""?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=d}_$AI(e,t=this,n,i){const s=this.strings;let o=!1;if(s===void 0)e=S(this,e,t,0),o=!P(e)||e!==this._$AH&&e!==w,o&&(this._$AH=e);else{const a=e;let l,c;for(e=s[0],l=0;l<s.length-1;l++)c=S(this,a[n+l],t,l),c===w&&(c=this._$AH[l]),o||(o=!P(c)||c!==this._$AH[l]),c===d?e=d:e!==d&&(e+=(c??"")+s[l+1]),this._$AH[l]=c}o&&!i&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Ke extends j{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}}class Ze extends j{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}}class Je extends j{constructor(e,t,n,i,s){super(e,t,n,i,s),this.type=5}_$AI(e,t=this){if((e=S(this,e,t,0)??d)===w)return;const n=this._$AH,i=e===d&&n!==d||e.capture!==n.capture||e.once!==n.once||e.passive!==n.passive,s=e!==d&&(n===d||i);i&&this.element.removeEventListener(this.name,this,n),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Xe{constructor(e,t,n){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(e){S(this,e)}}const Ye=R.litHtmlPolyfillSupport;Ye?.(M,k),(R.litHtmlVersions??(R.litHtmlVersions=[])).push("3.3.3");const et=(r,e,t)=>{const n=t?.renderBefore??e;let i=n._$litPart$;if(i===void 0){const s=t?.renderBefore??null;n._$litPart$=i=new k(e.insertBefore(N(),s),s,void 0,t??{})}return i._$AI(r),i};const I=globalThis;class O extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=et(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}}O._$litElement$=!0,O.finalized=!0,I.litElementHydrateSupport?.({LitElement:O});const tt=I.litElementPolyfillSupport;tt?.({LitElement:O});(I.litElementVersions??(I.litElementVersions=[])).push("4.2.2");const rt=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),nt=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),it={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function x(r){return String(r??"").trim().toLowerCase()}function xe(r){const e=x(r);return e?e.replaceAll("_"," "):""}function st(r){const e=x(r);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:it[e]??xe(e)}function ot(r){switch(r){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return xe(r)}}function at(r){if(x(r.queueRunState)!=="running")return null;const e=x(r.vacuumState),t=x(r.robotState),n=x(r.taskStatus),i=st(r.errorCode);if(e==="error")return{phase:"error",label:i??"Error"};if(n==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:i?`Paused (${i})`:"Paused"};if(rt.has(t))return{phase:"preparing",label:ot(t)};if(e==="returning"&&n==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(nt.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function q(r,e){const t=String(r||"").trim();if(!t.startsWith("vacuum."))return null;const n=t.slice(7);return n?`sensor.${n}_${e}`:null}const lt=10,ut=22,X={suction_level:{control:"select",suffix:"suction_level",options:["quiet","standard","strong","turbo"],optionIndexToOverrideValue:r=>r},water_volume:{control:"number",suffix:"wetness_level",values:[1,2,3],stateToOverrideValue:r=>{const e=Number(String(r??"").trim());return Number.isFinite(e)?e<=lt?1:e>=ut?3:2:null}}};function ct(r,e){const t=String(r||"").trim();if(!t.startsWith("vacuum."))return null;const n=t.slice(7);if(!n)return null;const i=X[e];return`${i.control}.${n}_${i.suffix}`}function dt(r,e){const t=X[r];if(t.control==="number")return t.stateToOverrideValue(e);const n=String(e??"").trim().toLowerCase(),i=t.options.indexOf(n);return i<0?null:t.optionIndexToOverrideValue(i)}function ht(r,e,t){return{domain:"ha_dreame",service:"update_running_override",data:{config_entry_id:r,field:e,value:pt(e,t)}}}function pt(r,e){const t=X[r];if(t.control==="number"){const o=t.stateToOverrideValue(e),a=o?t.values.indexOf(o):-1,l=a<0?0:(a+1)%t.values.length;return t.values[l]}const n=String(e??"").trim().toLowerCase(),i=t.options.indexOf(n),s=i<0?0:(i+1)%t.options.length;return t.optionIndexToOverrideValue(s)}function z(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function mt(r){return String(r??"").trim()}function we(r){return mt(r).toLowerCase()}function T(r){return typeof r!="number"||!Number.isFinite(r)||r<0?null:Math.trunc(r)}function he(r){return typeof r=="boolean"?r:null}function W(r,e){return r.filter(t=>t.status===e).length}function ft(r){if(!z(r))return null;const e=r.item_id,t=r.room_id,n=r.room_name,i=r.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof n!="string"||typeof i!="string"?null:{itemId:e,roomId:t,roomName:n,status:i,overrides:z(r.overrides)?{...r.overrides}:{},result:typeof r.result=="string"?r.result:null}}function Se(r){const e=we(r);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function vt(r){if(!z(r))return[];const e=r.queue_items;return Array.isArray(e)?e.flatMap(t=>{const n=ft(t);return n?[n]:[]}):[]}function _t(r){const e=r?.attributes,t=vt(e),n=z(e)?e:{};return{runState:we(r?.state)||"unknown",allowRobotCommands:he(n.allow_robot_commands),autoReconcileEnabled:he(n.auto_reconcile_enabled),configEntryId:typeof n.config_entry_id=="string"?n.config_entry_id:null,vacuumEntityId:typeof n.vacuum_entity_id=="string"?n.vacuum_entity_id:null,pendingItems:T(n.pending_items)??W(t,"pending"),runningItems:T(n.running_items)??W(t,"running"),completedItems:T(n.completed_items)??W(t,"completed"),totalItems:T(n.total_items)??t.length,items:t}}const Ee={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},gt={water_volume:2,suction_level:1,repeats:1};function Ce(r){if(r==null)return null;if(typeof r=="number")return Number.isFinite(r)?Math.trunc(r):null;if(typeof r=="string"){const e=Number(r.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function Re(r,e){const t={};for(const[n,i]of Object.entries(e??{}))i!=null&&(t[n]=i);for(const[n,i]of Object.entries(r??{}))i!=null&&(t[n]=i);return t}function bt(r,e,t){const n=Re(e,t);return Ce(n[r])??gt[r]}function Ie(r,e,t){const n=bt(r,e,t),i=Ee[r].find(s=>s.value===n);return i?i.label:String(n)}function $t(r,e,t){const n=Re(e,t),i=Ee[r],s=Ce(n[r]),o=i.findIndex(l=>l.value===s),a=o<0?0:(o+1)%i.length;return n[r]=i[a].value,n}function pe(r){if(typeof r=="number"&&Number.isInteger(r))return r;if(typeof r!="string")return null;const e=r.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function Q(r,e){if(Array.isArray(r)){for(const s of r)Q(s,e);return}if(typeof r!="object"||r===null)return;const t=r,n=pe(t.id),i=typeof t.name=="string"?t.name.trim():"";n!==null&&i&&e.push({roomId:n,roomName:i});for(const[s,o]of Object.entries(t)){const a=pe(s);if(a!==null&&typeof o=="string"){const l=o.trim();if(l){e.push({roomId:a,roomName:l});continue}}Q(o,e)}}function yt(r){const e=[];Q(r,e);const t=new Map;for(const n of e)t.set(n.roomId,n.roomName);return Array.from(t.entries()).map(([n,i])=>({roomId:n,roomName:i})).sort((n,i)=>n.roomId-i.roomId)}const D="ha-dreame-queue-card",At="ha-dreame-queue-card-editor",xt="HA Dreame Queue",wt="sensor.ha_dreame_queue_status",St=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}],Et=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"}];function Ct(r){return Object.entries(r?.states??{}).filter(([e,t])=>e.startsWith("sensor.")&&qt(t)).map(([e])=>e).sort()}function Rt(r){return{entity:Ct(r)[0]??wt}}function It(r,e){const t=ve(e.title)||xt,n=ve(e.entity)||null;if(!n)return me({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const i=r?.states[n];if(!i)return me({title:t,status:"missing",entityId:n,message:"Queue entity not found."});const s=_t(i),o=Ot(r,s),a=Ut(r,s);return{title:t,status:"ready",entityId:n,message:null,summary:kt(s,o),snapshot:s,activity:o,activeControls:Mt(s,o),canClearPending:s.pendingItems>0,rooms:a,rows:Nt(r,s)}}function me({title:r,status:e,entityId:t,message:n}){return{title:r,status:e,entityId:t,message:n,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function Ot(r,e){const t=e.vacuumEntityId;return!r||!t?null:at({queueRunState:e.runState,vacuumState:L(r,t),robotState:L(r,q(t,"state")),taskStatus:L(r,q(t,"task_status")),errorCode:L(r,q(t,"error"))})}function Nt(r,e){const t=e.items,n=Pt(r,e),i=t.flatMap((a,l)=>a.status==="pending"?[l]:[]),s=i[0]??null,o=i[i.length-1]??null;return t.map((a,l)=>({itemId:a.itemId,queuePosition:l,roomName:a.roomName,status:a.status,statusLabel:Se(a.status),...a.status==="running"&&n!==null?{progress:n}:{},overrides:{...a.overrides},canRemove:a.status==="pending",canMoveUp:a.status==="pending"&&l!==s,canMoveDown:a.status==="pending"&&l!==o,overrideControls:a.status==="pending"?Tt(a.overrides):Lt(r,e,a)}))}function Pt(r,e){const t=e.vacuumEntityId;if(!r||!t)return null;const n=q(t,"cleaning_progress"),i=fe(n?r.states[n]?.state:void 0);if(i!==null)return i;const s=r.states[t]?.attributes;return Y(s)?fe(s.cleaning_progress):null}function fe(r){if(r==null)return null;const e=Number(String(r).trim());return Number.isFinite(e)?Math.max(0,Math.min(100,Math.round(e))):null}function Mt(r,e){const t=r.allowRobotCommands===!1?{disabled:!0,disabledReason:"Robot commands disabled"}:{};return r.runState==="running"?e?.phase==="paused"||e?.phase==="error"?[{ariaLabel:"Continue robot run",label:"Continue",service:"resume_queue",...t},{ariaLabel:"End robot run",label:"End",service:"cancel_queue",...t}]:[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue",...t},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room",...t}]:r.runState==="idle"&&r.pendingItems>0?[{ariaLabel:"Start queue",label:"Start",service:"start_queue",...t}]:[]}function kt(r,e){if(e)return e.label;switch(r.runState){case"idle":return r.pendingItems===1?"Ready to start 1 room.":r.pendingItems>1?`Ready to start ${r.pendingItems} rooms.`:"Queue is empty.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access before restarting.";case"out_of_sync":return"Queue out of sync. Review robot state before restarting.";case"manual_control":return"Manual control active.";default:return`Queue state: ${Se(r.runState)}.`}}function Tt(r){return St.map(e=>({controlType:"pending",field:e.field,label:e.label,valueLabel:Ie(e.field,r,{})}))}function Lt(r,e,t){return!r||t.status!=="running"||!e.configEntryId||!e.vacuumEntityId?[]:Et.flatMap(n=>{const i=ct(e.vacuumEntityId??"",n.field);if(!i)return[];const s=r.states[i]?.state;if(s===void 0)return[];const o=dt(n.field,s);if(o===null)return[];const a=ht(e.configEntryId??"",n.field,s);return[{controlType:"running",field:n.field,label:n.label,valueLabel:Ie(n.field,{[n.field]:o},{}),value:a.data.value}]})}function Ut(r,e){const t=e.vacuumEntityId;if(!r||!t)return[];const n=r.states[t]?.attributes;return yt(Y(n)?n.rooms:void 0)}function L(r,e){return e?r.states[e]?.state:void 0}function ve(r){return String(r??"").trim()}function Y(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function qt(r){const e=r?.attributes;return Y(e)&&Array.isArray(e.queue_items)&&typeof e.config_entry_id=="string"}const V=class V extends O{constructor(){super(...arguments),this._config={}}static async getConfigElement(){return await Pe(()=>import("./ha-dreame-queue-card-editor-lXmQUl9-.js"),[]),document.createElement(At)}static getStubConfig(e){return Rt(e)}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 6}render(){const e=It(this.hass,this._config),t=e.snapshot,n=t?.configEntryId;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="activity-line">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          <div class="header-right">
            ${t?this._renderHeaderActions(e.activeControls,e.canClearPending,n):d}
            ${t?p`<span class="state-pill ${t.runState}"
                  >${this._stateLabel(t.runState)}</span
                >`:d}
          </div>
        </div>

        ${e.message?p`<div class="message">${e.message}</div>`:p`
              ${e.rooms.length?p`
                    <div class="section-title">Available rooms</div>
                    <div class="room-actions">
                      ${e.rooms.map(i=>p`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!n}
                            @click=${()=>this._addRoom(n,i.roomId,i.roomName)}
                          >
                            <ha-icon icon="mdi:plus"></ha-icon>
                            ${i.roomName}
                          </button>
                        `)}
                    </div>
                  `:d}
              <div class="queue-list">
                ${e.rows.length?e.rows.map(i=>p`
                        <div class="queue-item ${i.status}">
                          <div class="item-main">
                            <div class="item-headline">
                              <div class="item-title-block">
                                <span class="room-name"
                                  >${i.queuePosition+1}. ${i.roomName}</span
                                >
                                <span class="row-status ${i.status}">${i.statusLabel}</span>
                              </div>
                              ${this._renderQueueItemActions(i,n)}
                            </div>
                            ${i.overrideControls.length?p`
                                  <div class="item-actions">
                                    <div class="override-controls">
                                      ${i.overrideControls.map(s=>this._renderOverrideControl(i.roomName,i.itemId,i.overrides,s,n))}
                                    </div>
                                  </div>
                                `:d}
                            ${i.progress!==void 0?this._renderProgress(i.progress):d}
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
    `}_renderHeaderActions(e,t,n){return!e.length&&!t?d:p`
      <div class="header-actions">
        ${e.map(i=>p`
            <button
              aria-label=${i.ariaLabel}
              class="icon-btn ${i.service==="cancel_queue"?"delete":""}"
              title=${i.disabledReason??i.ariaLabel}
              type="button"
              ?disabled=${!n||i.disabled===!0}
              @click=${()=>this._callQueueService(n,i.service)}
            >
              <ha-icon icon=${this._activeControlIcon(i.service)}></ha-icon>
            </button>
          `)}
        ${t?p`
              <button
                aria-label="Clear pending queue"
                class="icon-btn"
                title="Clear pending queue"
                type="button"
                ?disabled=${!n}
                @click=${()=>this._clearPending(n)}
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
    `}_renderOverrideControl(e,t,n,i,s){return p`
      <button
        aria-label=${`Cycle ${e} ${this._overrideAriaField(i.field)}`}
        class="override-btn"
        title=${`${i.label}: ${i.valueLabel}`}
        type="button"
        ?disabled=${!s}
        @click=${()=>this._cycleOverride(s,t,n,i)}
      >
        <ha-icon icon=${this._overrideIcon(i.field,i.valueLabel)}></ha-icon>
        ${this._renderOverrideValue(i.field,i.valueLabel)}
      </button>
    `}_renderOverrideValue(e,t){if(e==="repeats")return p`<span>${t}</span>`;const n=e==="water_volume"?3:4;return this._renderBars(n,this._overrideActiveBars(e,t))}_renderBars(e,t){const n=Math.max(0,Math.min(e,t));return p`
      <span class="override-bars" aria-hidden="true">
        ${Array.from({length:e},(i,s)=>{const o=6+s*2,a=s<n;return p`
            <span
              class="override-bar ${a?"active":""}"
              style=${`height:${o}px;`}
            ></span>
          `})}
      </span>
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_activeControlIcon(e){return e==="start_queue"||e==="resume_queue"?"mdi:play":e==="skip_current_room"?"mdi:skip-next":"mdi:stop"}_overrideIcon(e,t){return e==="water_volume"?t==="Off"?"mdi:water-off":"mdi:water-percent":e==="suction_level"?t==="Off"?"mdi:fan-off":"mdi:fan":"mdi:repeat"}_overrideActiveBars(e,t){return t==="Off"?0:e==="water_volume"?{Min:1,Med:2,Max:3}[t]??0:e==="suction_level"?{Min:1,Med:2,Max:3,Turbo:4}[t]??0:0}_addRoom(e,t,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:n})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:n})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}_callQueueService(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame",t,{config_entry_id:e})}_updateOverrides(e,t,n,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:$t(n,i,{})})}_cycleOverride(e,t,n,i){if(i.controlType==="running"){this._updateRunningOverride(e,i.field,i.value);return}this._updateOverrides(e,t,i.field,n)}_updateRunningOverride(e,t,n){!e||!this.hass?.callService||t==="repeats"||n===void 0||this.hass.callService("ha_dreame","update_running_override",{config_entry_id:e,field:t,value:n})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};V.properties={hass:{attribute:!1},_config:{state:!0}},V.styles=ke`
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
  `;let G=V;customElements.get(D)||customElements.define(D,G);window.customCards=window.customCards??[];window.customCards.some(r=>r.type===D)||window.customCards.push({type:D,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});export{At as C,xt as D,ke as a,p as b,O as i,Ct as q};
