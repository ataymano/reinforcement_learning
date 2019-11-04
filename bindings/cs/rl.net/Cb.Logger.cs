﻿using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using Rl.Net.Native;

namespace Rl.Net
{
    namespace Native
    {
        // The publics in this class are just a verbose, but jittably-efficient way of enabling overriding a native invocation
        internal static partial class NativeMethods
        {
            [DllImport("rl.net.native.dll")]
            public static extern IntPtr CreateCbLogger(IntPtr config);

            [DllImport("rl.net.native.dll")]
            public static extern void DeleteCbLogger(IntPtr logger);

            [DllImport("rl.net.native.dll")]
            public static extern int CbLoggerInit(IntPtr logger, IntPtr apiStatus);

            [DllImport("rl.net.native.dll", EntryPoint = "CbLoggerLogF")]
            private static extern int CbLoggerLogFNative(IntPtr logger, IntPtr eventId, IntPtr contextJson, IntPtr rankingResponse, float outcome, IntPtr apiStatus);

            internal static Func<IntPtr, IntPtr, IntPtr, IntPtr, float, IntPtr, int> CbLoggerLogFOverride { get; set; }

            [DllImport("rl.net.native.dll", EntryPoint = "CbLoggerLogJson")]
            private static extern int CbLoggerLogJsonNative(IntPtr logger, IntPtr eventId, IntPtr contextJson, IntPtr rankingResponse, IntPtr outcome, IntPtr apiStatus);

            internal static Func<IntPtr, IntPtr, IntPtr, IntPtr, IntPtr, IntPtr, int> CbLoggerLogJsonOverride { get; set; }

            public static int CbLoggerLogF(IntPtr liveModel, IntPtr eventId, IntPtr contextJson, IntPtr rankingResponse, float outcome, IntPtr apiStatus)
            {
                if (CbLoggerLogFOverride != null)
                {
                    return CbLoggerLogFOverride(liveModel, eventId, contextJson, rankingResponse, outcome, apiStatus);
                }

                return CbLoggerLogFNative(liveModel, eventId, contextJson, rankingResponse, outcome, apiStatus);
            }

            public static int CbLoggerLogJson(IntPtr liveModel, IntPtr eventId, IntPtr contextJson, IntPtr rankingResponse, IntPtr outcome, IntPtr apiStatus)
            {
                if (CbLoggerLogJsonOverride != null)
                {
                    return CbLoggerLogJsonOverride(liveModel, eventId, contextJson, rankingResponse, outcome, apiStatus);
                }

                return CbLoggerLogJsonNative(liveModel, eventId, contextJson, rankingResponse, outcome, apiStatus);
            }

            [DllImport("rl.net.native.dll")]
            public static extern void CbLoggerSetCallback(IntPtr logger, [MarshalAs(UnmanagedType.FunctionPtr)] managed_background_error_callback_t callback = null);

            [DllImport("rl.net.native.dll")]
            public static extern void CbLoggerSetTrace(IntPtr logger, [MarshalAs(UnmanagedType.FunctionPtr)] managed_trace_callback_t callback = null);
        }
    }

    namespace Cb
    {
        public sealed class Logger : NativeObject<Logger>
        {
            private readonly NativeMethods.managed_background_error_callback_t managedErrorCallback;
            private readonly NativeMethods.managed_trace_callback_t managedTraceCallback;

            private static New<Logger> BindConstructorArguments(Configuration config)
            {
                return new New<Logger>(() => NativeMethods.CreateCbLogger(config.NativeHandle));
            }

            public Logger(Configuration config) : base(BindConstructorArguments(config), new Delete<Logger>(NativeMethods.DeleteCbLogger))
            {
                this.managedErrorCallback = new NativeMethods.managed_background_error_callback_t(this.WrapStatusAndRaiseBackgroundError);
                NativeMethods.CbLoggerSetCallback(this.NativeHandle, this.managedErrorCallback);

                this.managedTraceCallback = new NativeMethods.managed_trace_callback_t(this.SendTrace);
            }

            private static void CheckJsonString(string json)
            {
                if (String.IsNullOrWhiteSpace(json))
                {
                    throw new ArgumentException("Configuration json is empty", "json");
                }
            }

            unsafe private static int LoggerLogF(IntPtr liveModel, string eventId, string contextJson, IntPtr rankingResponse, float outcome, IntPtr apiStatus)
            {
                CheckJsonString(contextJson);

                fixed (byte* contextJsonUtf8Bytes = NativeMethods.StringEncoding.GetBytes(contextJson))
                {
                    IntPtr contextJsonUtf8Ptr = new IntPtr(contextJsonUtf8Bytes);

                    // It is important to pass null on faithfully here, because we rely on this to switch between auto-generate
                    // eventId and use supplied eventId at the rl.net.native layer.
                    if (eventId == null)
                    {
                        return NativeMethods.CbLoggerLogF(liveModel, IntPtr.Zero, contextJsonUtf8Ptr, rankingResponse, outcome, apiStatus);
                    }

                    fixed (byte* eventIdUtf8Bytes = NativeMethods.StringEncoding.GetBytes(eventId))
                    {
                        return NativeMethods.CbLoggerLogF(liveModel, new IntPtr(eventIdUtf8Bytes), contextJsonUtf8Ptr, rankingResponse, outcome, apiStatus);
                    }
                }
            }

            unsafe private static int LoggerLogJson(IntPtr liveModel, string eventId, string contextJson, IntPtr rankingResponse, string outcomeJson, IntPtr apiStatus)
            {
                CheckJsonString(contextJson);

                fixed (byte* contextJsonUtf8Bytes = NativeMethods.StringEncoding.GetBytes(contextJson))
                fixed (byte* outcomeJsonUtf8Bytes = NativeMethods.StringEncoding.GetBytes(outcomeJson))
                {
                    IntPtr contextJsonUtf8Ptr = new IntPtr(contextJsonUtf8Bytes);
                    IntPtr outcomeJsonUtf8Ptr = new IntPtr(outcomeJsonUtf8Bytes);

                    // It is important to pass null on faithfully here, because we rely on this to switch between auto-generate
                    // eventId and use supplied eventId at the rl.net.native layer.
                    if (eventId == null)
                    {
                        return NativeMethods.CbLoggerLogJson(liveModel, IntPtr.Zero, contextJsonUtf8Ptr, rankingResponse, outcomeJsonUtf8Ptr, apiStatus);
                    }

                    fixed (byte* eventIdUtf8Bytes = NativeMethods.StringEncoding.GetBytes(eventId))
                    {
                        return NativeMethods.CbLoggerLogJson(liveModel, new IntPtr(eventIdUtf8Bytes), contextJsonUtf8Ptr, rankingResponse, outcomeJsonUtf8Ptr, apiStatus);
                    }
                }
            }

            private void WrapStatusAndRaiseBackgroundError(IntPtr apiStatusHandle)
            {
                using (ApiStatus status = new ApiStatus(apiStatusHandle))
                {
                    EventHandler<ApiStatus> trargetEventLocal = this.BackgroundErrorInternal;
                    if (trargetEventLocal != null)
                    {
                        trargetEventLocal.Invoke(this, status);
                    }
                    else
                    {
                        // This comes strictly from the background thread - so simply throwing here has
                        // the right semantics with respect to AppDomain.UnhandledException. Unfortunately,
                        // that seems to bring down the process, if there is nothing Managed under the native
                        // stack this will cause an application-level unhandled native exception, and will
                        // likely terminate the application. So new up a thread, and throw from it.
                        // See https://stackoverflow.com/questions/42298126/raising-exception-on-managed-and-unmanaged-callback-chain-with-p-invoke

                        // IMPORTANT: This is safe solely because the status string is marshaled into the
                        // exception message on construction (in other words, before control returns to the
                        // unmanaged call-stack - the Dispose() is a no-op because in this case NativeObject does
                        // not own the unmanaged pointer, but we use it to remove itself from the finalizer queue)
                        RLException e = new RLException(status);
                        new System.Threading.Thread(() => throw e).Start();
                    }
                }
            }

            private void SendTrace(int logLevel, IntPtr msgUtf8Ptr)
            {
                string msg = NativeMethods.StringMarshallingFunc(msgUtf8Ptr);

                this.OnTraceLoggerEventInternal?.Invoke(this, new TraceLogEventArgs((RLLogLevel)logLevel, msg));
            }

            public bool TryInit(ApiStatus apiStatus = null)
            {
                int result = NativeMethods.CbLoggerInit(this.NativeHandle, apiStatus.ToNativeHandleOrNullptr());
                return result == NativeMethods.SuccessStatus;
            }

            public void Init()
            {
                using (ApiStatus apiStatus = new ApiStatus())
                    if (!this.TryInit(apiStatus))
                    {
                        throw new RLException(apiStatus);
                    }
            }

            public bool Log(string eventId, string contextJson, RankingResponse response, float outcome, ApiStatus apiStatus = null)
            {
                return this.TryLog(eventId, contextJson, response, outcome, apiStatus);
            }

            public bool TryLog(string eventId, string contextJson, RankingResponse response, float outcome, ApiStatus apiStatus = null)
            {
                int result = LoggerLogF(this.NativeHandle, eventId, contextJson, response.NativeHandle, outcome, apiStatus.ToNativeHandleOrNullptr());
                return result == NativeMethods.SuccessStatus;
            }

            public void Log(string eventId, string contextJson, RankingResponse response, float outcome)
            {
                using (ApiStatus apiStatus = new ApiStatus())
                    if (!this.TryLog(eventId, contextJson, response, outcome, apiStatus))
                    {
                        throw new RLException(apiStatus);
                    }
            }

            public bool Log(string eventId, string contextJson, RankingResponse response, string outcome, ApiStatus apiStatus = null)
            {
                return this.TryLog(eventId, contextJson, response, outcome, apiStatus);
            }

            public bool TryLog(string eventId, string contextJson, RankingResponse response, string outcome, ApiStatus apiStatus = null)
            {
                int result = LoggerLogJson(this.NativeHandle, eventId, contextJson, response.NativeHandle, outcome, apiStatus.ToNativeHandleOrNullptr());
                return result == NativeMethods.SuccessStatus;
            }

            public void Log(string eventId, string contextJson, RankingResponse response, string outcome)
            {
                using (ApiStatus apiStatus = new ApiStatus())
                    if (!this.TryLog(eventId, contextJson, response, outcome, apiStatus))
                    {
                        throw new RLException(apiStatus);
                    }
            }

            private event EventHandler<ApiStatus> BackgroundErrorInternal;

            // This event is thread-safe, because we do not hook/unhook the event in user-schedulable code anymore.
            public event EventHandler<ApiStatus> BackgroundError
            {
                add
                {
                    this.BackgroundErrorInternal += value;
                }
                remove
                {
                    this.BackgroundErrorInternal -= value;
                }
            }

            private event EventHandler<TraceLogEventArgs> OnTraceLoggerEventInternal;

            // TODO:
            /// <remarks>
            /// Add/remove here is not thread safe.
            /// </remarks>
            public event EventHandler<TraceLogEventArgs> TraceLoggerEvent
            {
                add
                {
                    if (this.OnTraceLoggerEventInternal == null)
                    {
                        NativeMethods.LiveModelSetTrace(this.NativeHandle, this.managedTraceCallback);
                    }

                    this.OnTraceLoggerEventInternal += value;
                }
                remove
                {
                    this.OnTraceLoggerEventInternal -= value;

                    if (this.OnTraceLoggerEventInternal == null)
                    {
                        NativeMethods.LiveModelSetTrace(this.NativeHandle, null);
                    }
                }
            }
        }
    }
}
